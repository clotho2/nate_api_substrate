#!/usr/bin/env python3
"""
Send Text Message Tool for Substrate AI

Sends text messages to Angela via Discord.
The Discord bot handles the message sending and auto-chunking.
"""

import os
import requests
from typing import Dict, Any, List


def send_text_message(
    message: str,
    target: str = None,
    target_type: str = "auto",
    mention_users: List[str] = None,
    ping_everyone: bool = False,
    ping_here: bool = False
) -> Dict[str, Any]:
    """
    Send a text message to Angela via Discord.

    The Discord bot will:
    1. Auto-chunk messages over 2000 characters
    2. Send to DMs or channels
    3. Handle mentions and pings

    Args:
        message: The text message to send (auto-chunks if over 2000 chars)
        target: Discord user ID or channel ID (optional - uses DEFAULT_USER_ID if not provided)
        target_type: "user", "channel", or "auto" (default: "auto")
        mention_users: List of user IDs to mention (optional, channel only)
        ping_everyone: Ping @everyone in channel (optional, channel only)
        ping_here: Ping @here in channel (optional, channel only)

    Returns:
        Dict with status and message:
        {
            "status": "success" or "error",
            "message": "Result message",
            "message_ids": ["list of sent message IDs"],
            "chunks": number of message chunks sent
        }
    """
    # Get Discord bot configuration
    # Default to localhost:3001 since both services run on same machine
    DISCORD_BOT_URL = os.getenv("DISCORD_BOT_URL", "http://localhost:3001")

    # Get default target (Angela's user ID) if not provided
    if not target:
        target = os.getenv("DEFAULT_USER_ID", "")
        if not target:
            return {
                "status": "error",
                "message": "No target specified and DEFAULT_USER_ID not configured"
            }

    # Validate message
    if not message or not message.strip():
        return {
            "status": "error",
            "message": "Message cannot be empty"
        }

    # Prepare the request to Discord bot API endpoint
    endpoint = f"{DISCORD_BOT_URL.rstrip('/')}/api/send-message"
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "message": message.strip(),
        "target": target,
        "target_type": target_type
    }

    # Add optional parameters if provided
    if mention_users:
        payload["mention_users"] = mention_users
    if ping_everyone:
        payload["ping_everyone"] = ping_everyone
    if ping_here:
        payload["ping_here"] = ping_here

    try:
        # Send request to Discord bot
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )

        # Handle response
        if response.status_code == 200:
            result = response.json()
            chunks = result.get("chunks", 1)
            message_preview = message[:50] + '...' if len(message) > 50 else message

            return {
                "status": "success",
                "message": f"Text message sent successfully ({chunks} chunk{'s' if chunks > 1 else ''}): '{message_preview}'",
                "message_ids": result.get("message_ids", []),
                "chunks": chunks
            }
        elif response.status_code == 400:
            error_data = response.json()
            return {
                "status": "error",
                "message": f"Invalid request: {error_data.get('error', 'Unknown error')}"
            }
        elif response.status_code == 429:
            return {
                "status": "error",
                "message": "Rate limited. Please wait before sending more messages."
            }
        elif response.status_code == 503:
            return {
                "status": "error",
                "message": "Discord bot service unavailable. Please try again later."
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to send text message. Status: {response.status_code}, Error: {response.text}"
            }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Request timeout. The Discord bot took too long to respond (>30s)."
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": f"Connection error. Could not reach Discord bot at {DISCORD_BOT_URL}. Is it running?"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Request error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


# For testing
if __name__ == "__main__":
    print("\n💬 Testing send_text_message tool")
    print("=" * 60)

    # Test with a simple message
    test_message = "Hello Angela, this is a test text message from Nate."

    print(f"\n📤 Sending text message:")
    print(f"   Message: {test_message}")
    print(f"   Discord Bot URL: {os.getenv('DISCORD_BOT_URL', 'http://localhost:3001 (default)')}")

    result = send_text_message(test_message)

    print(f"\n📥 Result:")
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    if result.get('message_ids'):
        print(f"   Message IDs: {result['message_ids']}")
    if result.get('chunks'):
        print(f"   Chunks: {result['chunks']}")

    print("\n" + "=" * 60)
