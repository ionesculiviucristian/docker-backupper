import smtplib
from email.message import EmailMessage

from src.notifiers.Notifier import Notifier


class Email(Notifier):
    def send_log_file(self, path: str) -> bool:
        return True

    def send_message(self, message: str) -> bool:
        try:
            hostname, external_ip = self.helpers["get_external_ip"]()

            msg = EmailMessage()
            msg["Subject"] = f"Backup errors on {hostname} {external_ip}"
            msg["From"] = self.config["notifiers"]["email"]["from_"]
            msg["To"] = ", ".join(self.config["notifiers"]["email"]["recipients"])
            msg.set_content(message)

            with smtplib.SMTP_SSL(
                self.config["notifiers"]["email"]["smtp"]["host"],
                self.config["notifiers"]["email"]["smtp"]["port"],
            ) as smtp:
                smtp.login(
                    self.config["notifiers"]["email"]["smtp"]["username"],
                    self.config["notifiers"]["email"]["smtp"]["password"],
                )
                smtp.send_message(msg)
            return True
        except Exception as e:
            self.log_manager.error(f"Unable to send email: {str(e)}")
            return False
