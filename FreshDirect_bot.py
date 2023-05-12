from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
import threading
import time

order_status = "InProcess"

# Define conversation states
inventory = {
    1: {'name': 'Apple', 'type': 'Fruit', 'brand': 'Fresh Farms', 'price': 0.99, 'weight': 'lb', 'quantity': 10},
    2: {'name': 'Banana', 'type': 'Fruit', 'brand': 'Chiquita', 'price': 0.25, 'weight': 'each', 'quantity': 20},
    3: {'name': 'Milk', 'type': 'Dairy', 'brand': 'Organic Valley', 'price': 2.99, 'weight': 'gal', 'quantity': 5},
    4: {'name': 'Eggs', 'type': 'Dairy', 'brand': 'Happy Eggs', 'price': 3.49, 'weight': 'dozen', 'quantity': 8},
    5: {'name': 'Bread', 'type': 'Bakery', 'brand': 'Wonder Bread', 'price': 1.99, 'weight': 'loaf', 'quantity': 12},
    6: {'name': 'Pasta', 'type': 'Pantry', 'brand': 'Barilla', 'price': 1.49, 'weight': 'lb', 'quantity': 15},
    7: {'name': 'Rice', 'type': 'Pantry', 'brand': 'Uncle Ben\'s', 'price': 2.99, 'weight': 'lb', 'quantity': 10},
    8: {'name': 'Chicken', 'type': 'Meat', 'brand': 'Perdue', 'price': 4.99, 'weight': 'lb', 'quantity': 6},
    9: {'name': 'Beef', 'type': 'Meat', 'brand': 'Angus', 'price': 8.99, 'weight': 'lb', 'quantity': 3},
    10: {'name': 'Salmon', 'type': 'Seafood', 'brand': 'Fresh Catch', 'price': 10.99, 'weight': 'lb', 'quantity': 4},
}

QUANTITY, ITEM_SELECTION = range(2)
orders = {}
SUGGESTION = ()

# Define callback functions for each command - working
def start(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user_name = update.message.from_user.first_name
    update.message.reply_text(f"Hi {user_name}, welcome to the grocery store! Type /order to begin.")
    update.message.reply_text("For User Manual, Type /help to gain detail information.")
    update.message.reply_text("To know list of features implemented, Type /feature. ")

def features(update: Updater, context: CallbackContext)->None:
    update.message.reply_text("The different features which are implemented as follows: ")
    update.message.reply_text("1. An Inventory of 10 items at users disposal.")
    update.message.reply_text("2. The cart will be shown everytime you add an item to cart so users dont overspend.")
    update.message.reply_text("3. Confirmation will be required from the user to finish the order. ")
    update.message.reply_text("4. Users can cancel the order anytime before pressing confirm button. ")
    update.message.reply_text("5. A suggestion box is made for the users to give any suggestions to the store owner. ")
    update.message.reply_text("6. A order tracking feature is implemented which tracks users order after every minute. ")
    update.message.reply_text("==== Future Updates ===")
    update.message.reply_text("1. Multilingual Bot which can converse in different languages. ")
    update.message.reply_text("2. Users can access the bot via different social media sites like facebook and instagram. ")
    update.message.reply_text("3. Making FreshDirect a global bot in supply chain and assisting not only shop owners but also delivery drivers.")

#working
def help(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("1. Type /order to begin ordering process.")
    update.message.reply_text("2. After you Type /order, Type /item_selection to select the item.")
    update.message.reply_text("3. After you Type /item_selection, Type item_id <space> item_quantity to order specified quantity.")
    update.message.reply_text("4. For example, if you want to buy 2 apples and item_id of apples is 1 then type 1 <space> 2.")
    update.message.reply_text("5. You will be displayed with your cart everytime.")
    update.message.reply_text("6.  After you have finished ordering, Type /confirm to confirm your order.")
    update.message.reply_text("7. If you wish to cancel your order anytime, Type /cancel to cancel your order.")
    update.message.reply_text("8. If you wish to see the inventory, Type /Inventory to check out the inventory.")
    update.message.reply_text("9. If you wish to suggest us something, Type /suggest.")
    update.message.reply_text("10. If you wish to see the features, Type /features.")
    update.message.reply_text("11. If you wish to see the tracking of your order, Type /order.")

#working
def order(update: Updater, context: CallbackContext) -> int:
    """Start the ordering process."""
    # Display inventory items
    inventory_message = "Inventory:\n"
    for item_id, item in inventory.items():
        inventory_message += f"{item['name']} ({item['type']}, {item['brand']}) - {item['price']} per {item['weight']} (Remaining: {item['quantity']})\n"
    inventory_message += "To select an item, type /item_selection."
    update.message.reply_text(inventory_message)

    # Set conversation state to QUANTITY
    return QUANTITY

#working
def item_selection(update: Updater, context: CallbackContext) -> int:
    """Prompt user to enter the item ID and quantity."""
    # Get item ID and quantity from user input
    try:
        item_id = int(update.message.text.split()[0])
        quantity = int(update.message.text.split()[1])

        update.message.reply_text(item_id)
        update.message.reply_text(quantity)

        user_id = update.effective_user.id
        if user_id not in orders:
            orders[user_id] = {}
        
            # Add item to cart
        if item_id in orders[user_id]:
            orders[user_id][item_id]['quantity'] += quantity
        else:
            orders[user_id][item_id] = {'name': inventory[item_id]['name'], 'price': inventory[item_id]['price'], 'quantity': quantity}

        # Display current cart and prompt user for next action
        cart_message = generate_cart_message(user_id)
        update.message.reply_text(cart_message)

        # Set conversation state to ITEM_SELECTION
        return ITEM_SELECTION


    except ValueError:
        get_suggestion(update,context)


#working
def get_chat_id(update):
    chat_id = update.message.chat_id
    #update.message.reply_text(f"Your chat ID is {chat_id}")
    return chat_id

def confirm(update: Updater, context: CallbackContext) -> int:
    """Confirm the order and send a message to the store owner."""
    user_id = update.effective_user.id
    if user_id not in orders:
        update.message.reply_text("You have not started an order yet. Type /order to begin.")
        return ConversationHandler.END
    # Generate a list of items in the user's cart and calculate the total cost
    item_list = "Your order:\n"
    total_cost = 0
    for item_id, item in orders[user_id].items():
        item_list += f"{item['quantity']} {inventory[item_id]['weight']} of {item['name']} - {item['price']} per {inventory[item_id]['weight']} = {item['price'] * item['quantity']}\n"
        total_cost += item['price'] * item['quantity']
    item_list += f"Total cost: {total_cost}\n"
    #item_list += "To confirm your order, please type /confirm.\n"
    #item_list += "To cancel your order, please type /cancel."
    update.message.reply_text(item_list)

    update.message.reply_text("The order has been placed. Sit Back and Enjoy your groceries being delivered to your doorstep.")
    update.message.reply_text("You can Type /start to order new groceries again or If you have any suggestions type /suggest.")
    global order_status
    order_status = "Ordered"

    # Send a message to the store owner to accept or decline the order
    #owner_message = f"New order:\n{item_list}"
    #context.bot.send_message(chat_id=get_chat_id(update), text=owner_message)

    # Set conversation state to QUANTITY and clear the user's cart
    orders[user_id] = {}
    return QUANTITY

#working
def cancel(update: Updater, context: CallbackContext) -> int:
    """Cancel the order and return to the start state."""
    orders[update.effective_user.id] = {}
    update.message.reply_text("Order cancelled. Type /order to start a new order.")
    return ConversationHandler.END

#working
def generate_cart_message(user_id: int) -> str:
    """Generate a message displaying the current cart."""
    cart_message = "Your cart:\n"
    for item_id, item in orders[user_id].items():
        cart_message += f"{item['name']} ({item['quantity']} {inventory[item_id]['weight']}) - {item['price']} per {inventory[item_id]['weight']}\n"
    cart_message += "To add more items to your cart, type /order."
    cart_message += "To check out and confirm your order, type /confirm."
    return cart_message

#working
def Inventory(update: Updater, context: CallbackContext) -> None:
    """Display the inventory."""
    inventory_message = "Inventory:\n"
    for item_id, item in inventory.items():
        inventory_message += f"{item['name']} ({item['type']}, {item['brand']}) - {item['price']} per {item['weight']} (Remaining: {item['quantity']})\n"
    update.message.reply_text(inventory_message)


def suggest(update, context):
    message = "Please type your suggestion:"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return "GET_SUGGESTION"

def get_suggestion(update, context):
    OWNER_CHAT_ID = get_chat_id(update)
    suggestion = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Thanks for your suggestion! It has been send to the store owner.")
    #context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"New suggestion received: {suggestion}")
    return ConversationHandler.END

def track_order(update, context):
    global order_status
    
    if order_status == "InProcess":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your order is currently in process. Please wait a while.")
    elif order_status == "Ordered":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your order has been confirmed and is being packed.")
    elif order_status == "Preparing":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your order has been packed and is being shipped.")
    elif order_status == "Shipped":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your order has been shipped and is out for delivery.")
    elif order_status == "Delivered":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your order has been delivered. Thank you for shopping with us!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, we could not find your order. Please try again later.")
    
def update_order_status(context):
    global order_status
    
    while True:
        if order_status == "Ordered":
            order_status = "Preparing"
        elif order_status == "Preparing":
            order_status = "Shipped"
        elif order_status == "Shipped":
            order_status = "Delivered"
        
        context.bot.send_message(chat_id=context.job.context, text="Order status updated to: {}".format(order_status))
        time.sleep(60)

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("6119032520:AAFvP9XQghuoFlyHzubevGUHKgZ3M7ZlPFQ", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Define conversation handler with entry points for /order, /confirm, and /cancel
    #conv_handler = ConversationHandler(
    #    entry_points=[CommandHandler("order", order)],
    ##    states={
    #  },
    #    fallbacks=[CommandHandler("cancel", cancel)],
    #)

    updater.dispatcher.add_handler(CommandHandler('suggest', suggest))

    conv_handler_suggestion = ConversationHandler(
    entry_points=[CommandHandler('order', order)],
    states={
        #"SELECT_ITEM": [MessageHandler(Filters.text, item_selection)],
        "GET_SUGGESTION": [MessageHandler(Filters.text, get_suggestion)],
        QUANTITY: [MessageHandler(Filters.text & ~Filters.command, item_selection)],
        ITEM_SELECTION: [MessageHandler(Filters.text & ~Filters.command, item_selection)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )

    updater.dispatcher.add_handler(conv_handler_suggestion)


    # Register the command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("confirm", confirm))
    dispatcher.add_handler(CommandHandler("inventory", Inventory))
    dispatcher.add_handler(CommandHandler("feature", features))
    dispatcher.add_handler(CommandHandler("track", track_order))
    
    #dispatcher.add_handler(conv_handler)
    job_queue = updater.job_queue
    job_queue.run_repeating(update_order_status, interval=60, first=60, context=dispatcher.bot)

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()

if __name__ == "__main__":
    main()
