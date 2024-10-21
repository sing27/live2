import os
import google.generativeai as genai
import dotenv
import time

dotenv.load_dotenv()

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


def image(newfile_path, text_message):
    # Upload the file and print a confirmation.
    sample_file = genai.upload_file(path=newfile_path,
                                display_name="Vision_Question")

    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    print("text : " + text_message)
    file = genai.get_file(name=sample_file.name)
    print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")

    while sample_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(5)
        sample_file = genai.get_file(sample_file.name)

    if sample_file.state.name == "FAILED":
        raise ValueError(sample_file.state.name)

    # Choose a Gemini model.
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    # Prompt the model with text and the previously uploaded image.
    response = model.generate_content([sample_file, text_message])

    imagemessage = response.text

    print(response.text)
    
    return imagemessage


if __name__ == "__main__":
    image()
