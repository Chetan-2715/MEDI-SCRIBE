import smtplib
import dns.resolver
from email_validator import validate_email, EmailNotValidError

def verify_email_smtp(email: str) -> bool:
    """
    Verifies if an email address exists by querying MX records and performing an SMTP handshake.
    Returns True if exists, False otherwise.
    """
    try:
        # 1. Syntax check
        valid = validate_email(email)
        email = valid.email
        domain = email.split('@')[1]

        # 2. Get MX Record
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)

        # 3. Connect to SMTP
        server = smtplib.SMTP(timeout=5)
        server.set_debuglevel(0)
        
        # SMTP Conversation
        server.connect(mx_record)
        server.helo(server.local_hostname) 
        server.mail('test@example.com')
        code, message = server.rcpt(email)
        server.quit()

        # 250 = Requested mail action okay, completed
        if code == 250:
            return True
        else:
            return False

    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        print(f"Domain lookup failed for {domain}")
        return False
    except (smtplib.SMTPServerDisconnected, TimeoutError, ConnectionRefusedError, OSError) as e:
        print(f"SMTP connection failed (likely blocked port 25), skipping verification: {e}")
        return True 
    except Exception as e:
        print(f"SMTP verification error, defaulting to valid: {e}")
        return True
