const typingForm = document.querySelector(".typing-form");
const chatList = document.querySelector(".chat-list");
const suggestions = document.querySelectorAll(".suggestion-list .suggestion");
const sttButton = document.querySelector("#stt-button");
const deleteChatButton = document.querySelector("#delete-chat-button");


let userMessage = null;
let isResponseGenerating = false;
let HaveImage = false;

const API_KEY = "AIzaSyBU_TXlDOQgvqHeIpR02LLuAQ17v5-65tw";
const API_URL = `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=${API_KEY}`;



const loadLocalstorageData = () => {

    const savedChats = localStorage.getItem("savedChats");
    const isLightMode = (localStorage.getItem("themeColor") === "light_mode");

    document.body.classList.toggle("light_mode", isLightMode);
    // sttButton.innerText = isLightMode ? "dark_mode" : "light_mode";


    chatList.innerHTML = savedChats || "";

    document.body.classList.toggle("hide-header", savedChats);
    chatList.scrollTo(0, chatList.scrollHeight);




}

loadLocalstorageData();

const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div");
    div.classList.add("message", ...classes);
    div.innerHTML = content;
    return div;


}

const showTypingEffect = (text, textElement, incomingMessageDiv) => {
    const words = text.split(' ');
    let currentWordIndex = 0;

    const typingInterval = setInterval(() => {
        textElement.innerText += (currentWordIndex === 0 ? ' ' : ' ') + words[currentWordIndex++];
        incomingMessageDiv.querySelector(".icon").classList.add("hide");



        if (currentWordIndex === words.length) {
            clearInterval(typingInterval);
            isResponseGenerating = false;
            incomingMessageDiv.querySelector(".icon").classList.remove("hide");
            localStorage.setItem("savedChats", chatList.innerHTML);
            chatList.scrollTo(0, chatList.scrollHeight);
        }

    }, 75);

}

const generateAPIResponse = async (incomingMessageDiv, query_text) =>    // generateAPIResponse generateAPIResponse

{


    const textElement = incomingMessageDiv.querySelector(".text");

    try {

        if (HaveImage === true) {
            const response01 = await fetch('/image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'chatId': 'asdasdasd', // place holder
                    'message': query_text,
                    'imageData': sessionStorage.getItem('image_data') // image have
                })
            });

            // const textElement= incomingMessageDiv.querySelector(".text");
            const result01 = await response01.json();
            const imageoutput = result01.message
            if (!response01.ok) {
                // console.error(response01)
                throw new Error(result01.message);
            }

            showTypingEffect(imageoutput, textElement, incomingMessageDiv);
            HaveImage = false;
            incomingMessageDiv.classList.remove("loading");
            sessionStorage.removeItem('image_data')
            return
        }

        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                contents: [{
                    role: "user",
                    parts: [{ text: userMessage }]
                }]

            })

        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error.message);

        const apiResponse = data?.candidates[0].content.parts[0].text.replace(/\*\*(.*?)\*\*/g, '$1');
        showTypingEffect(apiResponse, textElement, incomingMessageDiv);



        console.log(apiResponse)
        chatList.scrollTop = chatList.scrollHeight; // down

    } catch (error) {
        isResponseGenerating = false;
        textElement.innerText = error.message;
        textElement.classList.add("error");
        console.log(error);

    } finally {
        incomingMessageDiv.classList.remove("loading");

    }

}

const createAIMessageContentDiv = () => {
    const html = `<div class="message-content">
    <img src="/static/image/gemini.svg" alt="Gemini Image" class="avatar">
    <p class="text"></p>
    <div class="loading-indicator">
       <div class="loading-bar"></div>
       <div class="loading-bar"></div>
       <div class="loading-bar"></div>
    </div>
  </div>
  <span onclick="copyMessage(this)"  class="icon material-symbols-rounded">content_copy</span>`;
  return createMessageElement(html, "incoming", "loading");
}



const showLoadingAnimation = (query_text) => {
    const incomingMessageDiv = createAIMessageContentDiv();
    chatList.appendChild(incomingMessageDiv);
    chatList.scrollTo(0, chatList.scrollHeight);
    generateAPIResponse(incomingMessageDiv, query_text);
}


const copyMessage = (copyIcon) => {
    const messageText = copyIcon.parentElement.querySelector(".text").innerText;

    navigator.clipboard.writeText(messageText);
    copyIcon.innerText = "done";
    setTimeout(() => copyIcon.innerText = "content_copy", 1000);
}





const handleOutgoingChat = () => {
    userMessage = typingForm.querySelector(".typing-input").value.trim() || userMessage;
    if (!userMessage || isResponseGenerating) return;

    isResponseGenerating = true;


    const html = `<div class="message-content">
                    <p class="text">Lorem ipsum, dolor sit amet consectetur adipisicing elit. Iusto facere exercitationem quas nulla amet debitis, eos assumenda voluptatibus architecto minima nihil quidem accusantium quasi eum inventore illum autem impedit commodi!</p>
                      <img src="/static/image/image.jpg" alt="User Image" class="avatar">
                 </div>  `

    const outgoingMessageDiv = createMessageElement(html, "outgoing");
    outgoingMessageDiv.querySelector(".text").innerText = userMessage;
    chatList.appendChild(outgoingMessageDiv);

    typingForm.reset();
    chatList.scrollTo(0, chatList.scrollHeight);
    document.body.classList.add("hide-header");
    
    showLoadingAnimation(userMessage);
}

suggestions.forEach(suggestion => {
    suggestion.addEventListener("click", () => {
        userMessage = suggestion.querySelector(".text").innerText;
        handleOutgoingChat();
    });
});


sttButton.addEventListener("click", async () => {     // SSSSSSSSSSSSSSSSSSSSTTTTTTTTTTTTTTTTTTTTTTT
    const response = await fetch('/stt');
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const input = await response.json();
    userMessage = input.message || userMessage;
    console.log(input.message);  // 输出响应中的消息


    const html = `<div class="message-content">
      <p class="text">Lorem ipsum, dolor sit amet consectetur adipisicing elit. Iusto facere exercitationem quas nulla amet debitis, eos assumenda voluptatibus architecto minima nihil quidem accusantium quasi eum inventore illum autem impedit commodi!</p>
      <img src="/static/image/image.jpg" alt="User Image" class="avatar">
      </div>  `
    const outgoingMessageDiv = createMessageElement(html, "outgoing");
    outgoingMessageDiv.querySelector(".text").innerText = userMessage;
    chatList.appendChild(outgoingMessageDiv);

    chatList.scrollTo(0, chatList.scrollHeight);
    document.body.classList.add("hide-header");
    setTimeout(showLoadingAnimation, 500);

});



deleteChatButton.addEventListener("click", () => {
    if (confirm("Are you sure you want to delete all messages?"))
        localStorage.removeItem("savedChats");
    loadLocalstorageData();
});


typingForm.addEventListener("submit", (e) => {
    e.preventDefault();

    handleOutgoingChat();
})


const createFirstAIMessage = () => {
    let incomingMessageDiv = createAIMessageContentDiv();
    chatList.appendChild(incomingMessageDiv);
    chatList.scrollTo(0, chatList.scrollHeight);
    const textElement = incomingMessageDiv.querySelector(".text");
    showTypingEffect("Hello, How may I help you?", textElement, incomingMessageDiv);
    incomingMessageDiv.classList.remove("loading");
};

createAIMessageContentDiv();