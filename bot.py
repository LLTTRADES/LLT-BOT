import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import asyncio

# Constants
LLT_BNB_ADDRESS = "0x33eBc4E904277119820D84c91bFB31DAEadae698"
BSC_API_KEY = "X1NQJ56WEHAJQ4CUTRUFBPJDH4F1N37MQS"  # Replace with your BscScan API key
MINIMUM_BNB_MONTH = 0.15
MINIMUM_BNB_YEAR = 0.50

# Function to verify the transaction hash on BscScan
def verify_txn(txn_hash, min_bnb):
    url = f"https://api.bscscan.com/api"
    params = {
        "module": "transaction",
        "action": "gettxreceiptstatus",
        "txhash": txn_hash,
        "apikey": BSC_API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        if data["status"] == "1":  # Transaction successful
            # Fetch transaction details to confirm amount and recipient
            tx_details_url = f"https://api.bscscan.com/api"
            tx_details_params = {
                "module": "account",
                "action": "txlist",
                "address": LLT_BNB_ADDRESS,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "desc",
                "apikey": BSC_API_KEY
            }
            details_response = requests.get(tx_details_url, params=tx_details_params)
            if details_response.status_code == 200:
                transactions = details_response.json()["result"]
                for txn in transactions:
                    if txn["hash"] == txn_hash and txn["to"].lower() == LLT_BNB_ADDRESS.lower():
                        amount_bnb = float(txn["value"]) / (10**18)  # Convert Wei to BNB
                        if amount_bnb >= min_bnb:
                            return True, amount_bnb
                return False, None
            else:
                return False, None
        else:
            return False, None
    else:
        return False, None

# Function to handle the /start command
async def start(update: Update, context: CallbackContext):
    # Define the buttons for the start command
    keyboard = [
        [InlineKeyboardButton("Month with carefree Set-up@0.15BNB", callback_data="month")],
        [InlineKeyboardButton("One Year BEAST with LLT@0.50 BNB", callback_data="year")],
        [InlineKeyboardButton("Contact LLT Admins", callback_data="contact_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a welcome message with the buttons
    await update.message.reply_text(
        "Hello! Welcome to LLTTRADES bot. How can I assist you today?",
        reply_markup=reply_markup
    )

# Callback function to handle button clicks
async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Define the contact admin button that will always appear
    contact_admin_button = [
        [InlineKeyboardButton("Contact LLT Admins", callback_data="contact_admin")]
    ]
    contact_admin_markup = InlineKeyboardMarkup(contact_admin_button)

    # Handle the 'month' and 'year' button clicks
    if query.data == "month":
        await query.edit_message_text(
            text=(
                "Please provide your transaction hash to verify payment for the monthly subscription.\n\n"
                "⚠️ *Note:* Only send BNB Smart Chain (BNB) to the address:\n"
                f"{LLT_BNB_ADDRESS}\n\n"
                "After payment, reply here with `/verify_txn <your_txn_hash>`."
            ),
            parse_mode="Markdown",
            reply_markup=contact_admin_markup
        )
        context.user_data["min_bnb"] = MINIMUM_BNB_MONTH

    elif query.data == "year":
        await query.edit_message_text(
            text=(
                "Please provide your transaction hash to verify payment for the yearly subscription.\n\n"
                "⚠️ *Note:* Only send BNB Smart Chain (BNB) to the address:\n"
                f"{LLT_BNB_ADDRESS}\n\n"
                "After payment, reply here with `/verify_txn <your_txn_hash>`."
            ),
            parse_mode="Markdown",
            reply_markup=contact_admin_markup
        )
        context.user_data["min_bnb"] = MINIMUM_BNB_YEAR

    elif query.data == "contact_admin":
        # Send a message with the contact information
        await query.edit_message_text(
            text="For any queries, please contact the admins at: @Thugs007",
            reply_markup=contact_admin_markup
        )

# Function to handle the /verify_txn command
async def verify_txn_command(update: Update, context: CallbackContext):
    user_message = update.message.text.split()
    if len(user_message) != 2:
        await update.message.reply_text("Please provide a valid transaction hash. Example: `/verify_txn <txn_hash>`", parse_mode="Markdown")
        return

    txn_hash = user_message[1]
    min_bnb = context.user_data.get("min_bnb", MINIMUM_BNB_MONTH)  # Default to month subscription if not set

    # Verify the transaction hash
    is_valid, amount_bnb = verify_txn(txn_hash, min_bnb)
    if is_valid:
        await update.message.reply_text(
            text=(
                f"✅ Transaction verified successfully!\n\n"
                f"Amount: {amount_bnb:.2f} BNB\n\n"
                "Here is your VIP joining link:\n"
                "[VIP Group Link](https://t.me/+W3bQC7NQcMo4MTVk)"
            ),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text=(
                "❌ Transaction verification failed.\n\n"
                "*You naughty little trader, why did you try to bypass the subscription?*\n\n"
                "Please ensure you have sent at least the required amount of BNB to the correct address:\n"
                f"`{LLT_BNB_ADDRESS}`\n\n"
                "Feel free to contact admins for assistance."
            ),
            parse_mode="Markdown"
        )

# Main function to set up the bot
def main():
    # Use the provided token
    application = Application.builder().token("7733751857:AAF5OJrluNyHGfzCk3dmLSnZdRz_Z6rWj0s").build()

    # Register the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Register the button callback handler
    application.add_handler(CallbackQueryHandler(button_callback))

    # Register the /verify_txn command handler
    application.add_handler(CommandHandler("verify_txn", verify_txn_command))

    # Start polling for updates
    application.run_polling()

# Run the bot when the script is executed
if __name__ == '__main__':
    main()
