import smtplib
from email.message import EmailMessage

from src.notifiers.Notifier import Notifier
from src.typehints import TypeConfigNotifierEmail


class Email(Notifier[TypeConfigNotifierEmail]):
    def send_log_file(self, path: str) -> bool:
        return True

    def send_message(self, message: str) -> bool:
        try:
            hostname, external_ip = self.helpers["get_external_ip"]()

            msg = EmailMessage()
            msg["Subject"] = f"Backup errors on {hostname} {external_ip}"
            msg["From"] = self.config["from_"]
            msg["To"] = ", ".join(self.config["recipients"])
            msg.set_content(message)

            with smtplib.SMTP_SSL(
                self.config["smtp"]["host"],
                self.config["smtp"]["port"],
            ) as smtp:
                smtp.login(
                    self.config["smtp"]["username"],
                    self.config["smtp"]["password"],
                )
                smtp.send_message(msg)
            return True
        except Exception as e:
            self.log_manager.error(f"Unable to send email: {str(e)}")
            return False
