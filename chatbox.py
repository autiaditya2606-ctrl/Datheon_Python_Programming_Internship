
import json
import re


# Load FAQ data from the JSON file
def load_faq(filename="faq.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Warning: Could not load FAQ data: {error}")
        return {}


# Normalize user input
def normalize_input(text):
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


# Identify the user's intent
def identify_intent(message):
    # Exit commands
    if re.fullmatch(r"(bye|exit|quit|goodbye)[.! ]*", message):
        return "exit"

    # Greeting patterns
    if re.search(
        r"\b(hi|hello|hey|good morning|good afternoon)\b",
        message
    ):
        return "greeting"

    # Business hours
    if re.search(
        r"\b(hours|opening|closing|open|closed|working hours)\b",
        message
    ):
        return "business_hours"

    # Product-related FAQ keywords
    if re.search(
        r"\b(shipping|delivery|deliver|return|refund|exchange|"
        r"payment|pay|card|warranty|guarantee)\b",
        message
    ):
        return "faq"

    # General product questions
    if re.search(
        r"\b(product|products|price|cost|features)\b",
        message
    ):
        return "product"

    return "unknown"


# Find the relevant FAQ answer
def find_faq_answer(message, faq):
    for topic, details in faq.items():
        if topic == "business_hours":
            continue

        keywords = details.get("keywords", [])

        for keyword in keywords:
            if re.search(
                rf"\b{re.escape(keyword.lower())}\b",
                message
            ):
                return details["answer"]

    return None


# Generate a response
def get_response(message, faq, state):
    message = normalize_input(message)
    intent = identify_intent(message)

    if intent == "exit":
        return "Thank you for contacting us. Goodbye!", "exit"

    if intent == "greeting":
        return (
            "Hello! Welcome to customer support. "
            "How can I help you today?",
            "intent_identification"
        )

    if intent == "business_hours":
        hours = faq.get("business_hours", {})
        answer = hours.get(
            "answer",
            "Sorry, our business hours are currently unavailable."
        )
        return answer, "resolution"

    if intent == "faq":
        answer = find_faq_answer(message, faq)

        if answer:
            return answer, "resolution"

        return (
            "Could you clarify whether you need help with shipping, "
            "returns, payments, or warranty?",
            "intent_identification"
        )

    if intent == "product":
        return (
            "I can help with product information. "
            "Which product or feature would you like to know about?",
            "intent_identification"
        )

    return (
        "I'm sorry, I didn't understand that. "
        "You can ask about business hours, shipping, returns, "
        "payments, or warranty.",
        "intent_identification"
    )


# Main chatbot loop
def main():
    faq = load_faq()

    print("=" * 45)
    print("Welcome to Customer Support Chatbot!")
    print("Type 'bye', 'exit', or 'quit' to end.")
    print("=" * 45)

    state = "greeting"

    while state != "exit":
        user_input = input("\nYou: ").strip()

        if not user_input:
            print("Bot: Please enter a question.")
            continue

        response, state = get_response(user_input, faq, state)
        print("Bot:", response)

    print("Chat session ended.")


if __name__ == "__main__":
    main()
