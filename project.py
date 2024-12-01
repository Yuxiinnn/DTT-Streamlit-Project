import streamlit as st
import random
import speech_recognition as sr
import pyttsx3

# Function to generate a greeting message
def greet_user():
    greetings = [
        "Hello! Thank you for choosing Talk2Order! Would you like to dine in or take away?",
        "Welcome to Talk2Order! Would you like to dine in or take away?"
    ]
    return random.choice(greetings)

# Function to speak the text
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Text-to-speech initialization error: {str(e)}")

# Menu items with prices
menu_items = {
    "Burgers": {
        "Big Mac": 7.00,
        "Cheeseburger": 3.90,
        "McChicken": 3.65,
        "Filet-O-Fish": 4.80,
        "Quarter Pounder with Cheese": 7.00
    },
    "Fries": {
        "Small Fries": 2.85,
        "Medium Fries": 3.95,
        "Large Fries": 4.20
    },
    "Drinks": {
        "Coke": 2.95,
        "Sprite": 2.95,
        "Fanta": 2.95,
        "Iced Milo": 3.80,
    },
    "Sides": {
        "6 pieces Chicken Nuggets": 5.75,
        "20 pieces Chicken Nuggets": 13.70,
        "Banana Pie": 1.85,
        "Apple Pie": 2.10
    },
    "Desserts": {
        "Strawberry Shortcake McFlurry": 4.00,
        "Oreo McFlurry": 3.60,
        "Hot Fudge Sundae": 2.80,
        "Soft Serve Cone": 1.20
    }
}

# Function to recognize speech
def recognize_speech(prompt=""):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if prompt:
            speak(prompt)  # Speak the prompt
            st.write(prompt)  # Display the prompt in Streamlit

        with st.spinner("Listening..."):
            try:
                audio = recognizer.listen(source, timeout=15)
                order = recognizer.recognize_google(audio)  # Use Google Speech Recognition
                return order
            except sr.WaitTimeoutError:
                st.error("Listening timed out. Please try again.")
                return None
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your speech.")
                return None
            except sr.RequestError:
                st.error("Could not request results from the speech recognition service.")
                return None

# Main application
def main():
    st.title("AI Voice Ordering Kiosk")

    # Display a greeting message and ask if the user wants to dine in or take away
    greeting = greet_user()
    st.write(greeting)
    speak(greeting)

    # Variable to store the dining choice
    dining_choice = None

    # Loop until a valid dining choice is made
    while dining_choice is None:
        dining_order = recognize_speech()
        if dining_order:
            dining_order_lower = dining_order.lower()
            dine_in_variants = ["dine in", "dining in", "eating in", "eat in"]
            take_away_variants = ["take away", "takeout"]

            if any(variant in dining_order_lower for variant in dine_in_variants):
                dining_choice = "Dine in"
                st.write("You chose: Dine in.")
            elif any(variant in dining_order_lower for variant in take_away_variants):
                dining_choice = "Take away"
                st.write("You chose: Take away.")
            else:
                st.warning("Invalid choice. Please repeat your choice.")
                speak("Invalid choice. Please repeat your choice.")

    # Proceed with the ordering process after a valid dining choice is made
    total_cost = 0
    order_details = {
        "Burger": None,
        "Fries": None,
        "Drink": None,
        "Sides": None,
        "Dessert": None
    }

    # Display the menu items
    st.header("Menu Items")
    for category, items in menu_items.items():
        st.subheader(category)
        for item, price in items.items():
            st.write(f"{item}: ${price:.2f}")

    # Sequentially prompt for each category
    for category in ["Burgers", "Fries", "Drinks", "Sides", "Desserts"]:
        found = False
        prompt_message = f"Please say your {category.lower()}."
        st.header(prompt_message)
        speak(prompt_message)

        while not found:  # Keep asking until a valid item is found
            order = recognize_speech()
            if order:
                order_lower = order.lower()

                # Check if the user said "none"
                if "none" in order_lower:
                    order_details[category[:-1]] = "None"
                    found = True
                    st.write(f"No {category.lower()} added to your order.")
                    break  # Exit the loop if "none" is detected

                # Enhanced matching for sides to improve detection
                if category == "Sides":
                    side_variants = {
                        "6 pieces Chicken Nuggets": ["six pieces of chicken nuggets", "six pieces chicken nuggets", "6 pieces of chicken nuggets", "6 pieces chicken nuggets"],
                        "20 pieces Chicken Nuggets": ["twenty pieces of chicken nuggets", "twenty pieces chicken nuggets", "20 pieces of chicken nuggets", "20 pieces chicken nuggets"],
                        "Banana Pie": ["banana pie"],
                        "Apple Pie": ["apple pie"]
                    }
                    for item, variants in side_variants.items():
                        for variant in variants:
                            if variant in order_lower or order_lower in variant:
                                order_details[category] = item  # Remove the last character for key
                                total_cost += menu_items[category][item]
                                found = True
                                st.write(f"Found {item} in order!")
                                break  # Exit loop once an item is found
                    if found:
                        break  # Exit outer loop if item found

                # Enhanced matching for fries to improve detection
                elif category == "Fries":
                    for item in menu_items[category].keys():
                        if item.lower() in order_lower or order_lower in item.lower():
                            order_details["Fries"] = item  # Remove the last character for key
                            total_cost += menu_items[category][item]
                            found = True
                            st.write(f"Found {item} in order!")
                            break  # Exit loop once an item is found

                else:
                    for item, price in menu_items[category].items():
                        if item.lower() in order_lower or order_lower in item.lower():
                            order_details[category[:-1]] = item  # Remove the last character for key
                            total_cost += price
                            found = True
                            st.write(f"Found {item} in order!")
                            break  # Exit loop once an item is found

            if not found:
                st.warning(f"No valid {category.lower()} found. Please repeat your {category.lower()}.")
                speak(f"No valid {category.lower()} found. Please repeat your {category.lower()}.")

    # Prepare confirmation message
    confirmation_message = "Your order has been placed:\n"
    confirmation_message += f"\nBurger: {order_details['Burger'] if order_details['Burger'] else 'None'}\n"
    confirmation_message += f"\nFries: {order_details['Fries'] if order_details['Fries'] else 'None'}\n"
    confirmation_message += f"\nDrink: {order_details['Drink'] if order_details['Drink'] else 'None'}\n"
    confirmation_message += f"\nSides: {order_details['Sides'] if order_details['Sides'] else 'None'}\n"
    confirmation_message += f"\nDessert: {order_details['Dessert'] if order_details['Dessert'] else 'None'}\n"
    confirmation_message += f"\nTotal Cost: ${total_cost:.2f}"

    st.success(confirmation_message)
    speak(confirmation_message)

    # Payment method selection using voice
    payment_prompt = "Please say your payment method: Credit Card, Debit Card, or Cash."
    st.write(payment_prompt)
    speak(payment_prompt)

    payment_method = None

    while payment_method is None:  # Keep asking for a valid payment method
        payment_input = recognize_speech()
        if payment_input:
            payment_input = payment_input.lower()
            if "credit card" in payment_input:
                payment_method = "Credit Card"
            elif "debit card" in payment_input:
                payment_method = "Debit Card"
            elif "cash" in payment_input:
                payment_method = "Cash"
            else:
                st.warning("Invalid payment method. Please repeat your payment method.")
                speak("Invalid payment method. Please repeat your payment method.")

    st.write(f"You chose to pay by: {payment_method}.")
    speak(f"You chose to pay by: {payment_method}.")

    # Thank You message based on payment method
    if payment_method in ["credit card", "debit card"]:
        thank_you_message = "Your Order Number: 6940\n \nThank you for your order!\n \nHave a great day and hope to see you again!"
    else:  # If payment method is cash
        thank_you_message = "Please proceed to the counter to confirm your order\nThank you for your order!\n \nHave a great day and hope to see you again!"

    st.success(thank_you_message)
    speak(thank_you_message)

if __name__ == "__main__":
    main()
