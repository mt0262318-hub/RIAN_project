import logging
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger("ingress_router")
ingress_bp = APIRouter(prefix="/ingress", tags=["Ingress Channels"])

class EmailPayload(BaseModel):
    sender: str
    subject: str
    body: str
    message_id: Optional[str] = None

@ingress_bp.post("/twilio/voice")
async def twilio_voice_webhook(request: Request):
    """
    Handles inbound voice calls from Twilio.
    Returns standard TwiML XML to speak back to the caller.
    """
    form_data = await request.form()
    caller = form_data.get("From", "Unknown")
    speech_result = form_data.get("SpeechResult", None)
    
    logger.info(f"📞 Inbound Call from: {caller} | Query: {speech_result}")
    
    if speech_result:
        # User spoke something -> AI Response simulation
        reply_text = f"Hello. Rian system received your command: {speech_result}. Processing request."
    else:
        # Initial greeting when phone picks up
        reply_text = "Namaste, this is Rian Autonomous System. How can I assist you today?"

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="en-IN">{reply_text}</Say>
    <Gather input="speech" timeout="5" action="/ingress/twilio/voice" method="POST" />
</Response>"""

    return Response(content=twiml_response, media_type="application/xml")


@ingress_bp.post("/email/hook")
async def email_inbound_webhook(payload: EmailPayload):
    """
    Handles inbound parsed emails (SendGrid / Mailgun / Webhook).
    """
    logger.info(f"📧 Inbound Email from {payload.sender} - Subject: {payload.subject}")
    # Process through RIAN agent memory
    return {
        "status": "success",
        "processed": True,
        "sender": payload.sender,
        "message": "Email ingested into RIAN processing pipeline."
    }
