import json
import imaplib
import email
from email.header import decode_header

def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    
    username = config["username"]
    password = config["password"]
    imap_server = config["imap_server"]
    port = config["port"]
    ignorefolder = config["ignorefolder"]
    #mailsignore = config["mailsignore"]

    #load mailignore from .mailignore file
    with open(".mailignore", "r") as f:
        mailsignore = f.read().splitlines()

    return username, password, imap_server, port, ignorefolder, mailsignore

def main():
    nb = 0

    print("MailIgnore v0.1")
    #print("Loading configuration...")
    username, password, imap_server, port, ignorefolder, mailsignore = load_config()
    #print("Configuration loaded.")
    #print("Connecting to IMAP server...")
    imap = imaplib.IMAP4_SSL(imap_server, port)
    imap.login(username, password)
    #print("Connected.")
    #print("Selecting INBOX...")
    imap.select("INBOX")
    #print("Selected.")
    #print("Searching for unread messages...")

    status, messages = imap.search(None, 'ALL')
    #print("Messages found.")
    #print("Processing messages...")

    #print(messages)

    # Loop through each email ID returned by the search
    for msg_id in messages[0].split():
        # Fetch the email using its ID
        status, data = imap.fetch(msg_id, '(RFC822)')
        
        # Parse the email content
        raw_email = data[0][1]
        
        try:
            email_message = email.message_from_bytes(raw_email)
        except:
            None
        
        # Extract email information
        subject = email_message['Subject']
        from_email = email_message['From']
        to_email = email_message['To']
        
        # Decode email subject if needed
        #subject = decode_header(subject)[0][0]
        #if isinstance(subject, bytes):
        #    subject = subject.decode()

        if to_email is None:
            continue
        if any (string in to_email for string in mailsignore):
            # Move the email to the MAILALL folder
            imap.copy(msg_id, ignorefolder)
            imap.store(msg_id, '+FLAGS', '\\Deleted')
            imap.expunge()
            #print(f"Moved email from {from_email} with subject {subject} to MAILALL.")
            imap.store(msg_id, '-FLAGS', '\\Seen')
            nb += 1

    #print("Logging out...")
    imap.logout()
    #print("Logged out.")
    #print("MailIgnore finished.")
    print(f"{nb} emails moved to {ignorefolder}.")

if __name__ == "__main__":
    main()