"""
Token usage control utilities
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException

from open_webui.models.users import Users, UserModel
from open_webui.config import (
    ENABLE_TOKEN_USAGE_CONTROL,
    TOKEN_INITIAL_AMOUNT,
    TOKEN_REPLENISH_INTERVAL,
    TOKEN_REPLENISH_AMOUNT,
)

log = logging.getLogger(__name__)


def is_token_usage_enabled() -> bool:
    """Check if token usage control is enabled"""
    return ENABLE_TOKEN_USAGE_CONTROL.value


def get_token_config() -> Dict[str, int]:
    """Get current token configuration"""
    return {
        "initial_amount": TOKEN_INITIAL_AMOUNT.value,
        "replenish_interval": TOKEN_REPLENISH_INTERVAL.value,
        "replenish_amount": TOKEN_REPLENISH_AMOUNT.value,
    }


def initialize_user_tokens(user_id: str) -> bool:
    """Initialize tokens for a new user"""
    if not is_token_usage_enabled():
        return True
    
    initial_amount = TOKEN_INITIAL_AMOUNT.value
    success = Users.initialize_user_tokens(user_id, initial_amount)
    
    if success:
        log.info(f"Initialized {initial_amount} tokens for user {user_id}")
    else:
        log.error(f"Failed to initialize tokens for user {user_id}")
    
    return success


def check_and_consume_tokens_before_request(user: UserModel, estimated_tokens: int = 100) -> bool:
    """
    Check if user can make a request. Only blocks if balance is 0 or negative.
    Args:
        user: The user making the request
        estimated_tokens: Estimated tokens needed (not used for blocking)
    Returns:
        True if user can proceed, False otherwise
    """
    if not is_token_usage_enabled():
        return True
    
    if user.role == "admin":
        return True  # Admin users have unlimited tokens
    
    # Get current user to check actual balance
    current_user = Users.get_user_by_id(user.id)
    if not current_user:
        return False
    
    # Only block if balance is 0 or negative, check for replenishment
    if current_user.token_balance <= 0:
        config = get_token_config()
        can_consume, was_replenished = Users.can_user_consume_tokens(
            user.id,
            1,  # Just need 1 token to proceed
            config["replenish_interval"],
            config["replenish_amount"]
        )
        
        if was_replenished:
            log.info(f"Replenished {config['replenish_amount']} tokens for user {user.id}")
            return True
        else:
            log.warning(f"User {user.id} has no tokens and cannot be replenished yet")
            return False
    
    # User has positive balance, allow the request (balance can go negative after usage)
    return True


def consume_tokens_after_response(user: UserModel, usage_data: Dict[str, Any]) -> bool:
    """
    Consume tokens after getting the actual usage from the response.
    Balance can go negative.
    Args:
        user: The user who made the request
        usage_data: Usage data from the model response
    Returns:
        True if tokens were successfully consumed
    """
    if not is_token_usage_enabled():
        return True
    
    if user.role == "admin":
        return True  # Admin users have unlimited tokens
    
    # Extract total tokens from usage data
    total_tokens = usage_data.get("total_tokens", 0)
    
    if total_tokens <= 0:
        # Fallback to sum of prompt and completion tokens
        prompt_tokens = usage_data.get("prompt_tokens", 0)
        completion_tokens = usage_data.get("completion_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens
    
    if total_tokens <= 0:
        log.warning(f"No token usage data found for user {user.id}")
        return True  # Don't block if we can't determine usage
    
    # Get current balance before deduction for logging
    current_user = Users.get_user_by_id(user.id)
    current_balance = current_user.token_balance if current_user else 0
    
    success = Users.deduct_user_tokens_by_id(user.id, total_tokens)
    
    if success:
        new_balance = current_balance - total_tokens
        log.info(f"Consumed {total_tokens} tokens for user {user.id} (balance: {current_balance} -> {new_balance})")
    else:
        log.error(f"Failed to consume {total_tokens} tokens for user {user.id}")
    
    return success


def get_user_token_info(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's token usage information"""
    try:
        user = Users.get_user_by_id(user_id)
        if not user:
            return None
        
        return {
            "token_balance": user.token_balance,
            "total_tokens_used": user.total_tokens_used,
            "last_token_replenish_time": user.last_token_replenish_time,
            "usage_control_enabled": is_token_usage_enabled(),
        }
    except Exception as e:
        log.error(f"Error getting token info for user {user_id}: {e}")
        return None


def admin_update_user_tokens(user_id: str, new_balance: int) -> bool:
    """Admin function to update user token balance"""
    success = Users.update_user_token_balance_by_id(user_id, new_balance)
    
    if success:
        log.info(f"Admin updated token balance to {new_balance} for user {user_id}")
    else:
        log.error(f"Failed to update token balance for user {user_id}")
    
    return success


def raise_insufficient_tokens_error():
    """Raise an HTTP exception for insufficient tokens"""
    raise HTTPException(
        status_code=429,
        detail="You have insufficient tokens to complete this request. Please wait for token replenishment or contact an administrator."
    )