import logging
from schemas.auth import UserInfo

logger = logging.getLogger(__name__)

class EmailService:
    async def send_verification_email(self, user: UserInfo, token: str):
        """
        Simulates sending a verification email.
        In a real application, this would use a service like SendGrid or Amazon SES.
        """
        verification_link = f"http://localhost:8000/apps/auth/verify_email?token={token}"
        
        # Log the email content instead of sending it
        logger.info("---BEGIN MOCK EMAIL---")
        logger.info(f"To: {user.email}")
        logger.info("From: no-reply@01agent.ai")
        logger.info("Subject: Verify Your Email Address")
        logger.info("")
        logger.info(f"Hi {user.name},")
        logger.info("")
        logger.info("Thanks for signing up for 01Agent! Please verify your email address by clicking the link below:")
        logger.info(verification_link)
        logger.info("")
        logger.info("Thanks,")
        logger.info("The 01Agent Team")
        logger.info("---END MOCK EMAIL---")
        
        # In a real implementation, you would have something like:
        #
        # import sendgrid
        # from sendgrid.helpers.mail import Mail
        #
        # message = Mail(
        #     from_email='no-reply@01agent.ai',
        #     to_emails=user.email,
        #     subject='Verify Your Email Address',
        #     html_content=f'<strong>Please verify your email address by clicking <a href="{verification_link}">here</a>.</strong>'
        # )
        # try:
        #     sg = sendgrid.SendGridAPIClient('YOUR_SENDGRID_API_KEY')
        #     response = await sg.send(message)
        #     logger.info(f"Verification email sent to {user.email}, status code: {response.status_code}")
        # except Exception as e:
        #     logger.error(f"Failed to send verification email: {e}")
        #     raise
