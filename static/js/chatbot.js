const typingForm = document.querySelector(".typing-form");
const chatList = document.querySelector(".chat-list");
const suggestions = document.querySelectorAll(".suggestion-list .suggestion");
const sttButton = document.querySelector("#stt-button");
const deleteChatButton = document.querySelector("#delete-chat-button");
const hello2title = document.querySelector(".hello2");

const imageChatButton = document.querySelector("#attachment");
const uploadModal = document.getElementById('uploadModal');
const closeModalButton = document.getElementById('closeModal');
const uploadForm = document.getElementById('uploadForm');

let userMessage = null;
let isResponseGenerating = false;
let videoresult = null;
let multimedia = [];
let latitude = "";
let longitude = "";
let userlocation = "";

window.addEventListener('load', () => {
    sessionStorage.clear(); // 清除 sessionStorage
    videoresult = null;
});

const loadLocalstorageData = () => {

    const savedChats = localStorage.getItem("savedChats");
    const isLightMode = (localStorage.getItem("themeColor") === "light_mode");

    document.body.classList.toggle("light_mode", isLightMode);
    // sttButton.innerText = isLightMode ? "dark_mode" : "light_mode";


    chatList.innerHTML = savedChats || "";

    document.body.classList.toggle("hide-header", savedChats);
    chatList.scrollTo(0, chatList.scrollHeight);

}

// loadLocalstorageData();


const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div");
    div.classList.add("message", ...classes);
    div.innerHTML = content;
    return div;

}

const showTypingEffect = async (text, textElement, incomingMessageDiv) => {
    console.log(text)
    const words = text.split(' ');
    let currentWordIndex = 0;

    const typingInterval = setInterval(() => {
        textElement.innerText += (currentWordIndex === 0 ? ' ' : ' ') + words[currentWordIndex++];
        incomingMessageDiv.querySelector(".icon").classList.add("hide");



        if (currentWordIndex === words.length) {
            clearInterval(typingInterval);
            isResponseGenerating = false;
            incomingMessageDiv.querySelector(".icon").classList.remove("hide");
            incomingMessageDiv.querySelector(".chattime").style.display = 'block';
            localStorage.setItem("savedChats", chatList.innerHTML);
            chatList.scrollTo(0, chatList.scrollHeight);
        }

    }, 75);

}

const speakAndTypeResponse = async (typingData, audioData) => {
    showTypingEffect(typingData.imageoutput, typingData.textElement, typingData.incomingMessageDiv);
    talk(audioData.model, `data:audio/wav;base64,${audioData.audioText}`) // !! 

}



const generateAPIResponse = async (incomingMessageDiv, query_text) =>    // generateAPIResponse

{
    const textElement = incomingMessageDiv.querySelector(".text");

    // const VideoData = (videoresult != null) ? videoresult : sessionStorage.getItem("image_data") || null;
    const VideoData = multimedia;
    console.log(VideoData)

    const response01 = await fetch('/chat_api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'message': query_text,
            'imageData': VideoData, // image have
            'context': {
                'chatId': 'abc', // place holder
                'location': `${latitude},${longitude}` // image have
            }
        })
    });

    const result01 = await response01.json();
    const imageoutput = result01.message
    console.log(imageoutput)
    const audioOutput = result01.ttsAudio // !! 

    await speakAndTypeResponse({
        imageoutput: imageoutput,
        textElement: textElement,
        incomingMessageDiv: incomingMessageDiv,
    }, {
        model: model4,
        audioText: audioOutput  // !!
    });

    incomingMessageDiv.classList.remove("loading");
    sessionStorage.removeItem('image_data');
    videoresult, userMessage = null;
    multimedia = [];
    console.log("reset sessionStorage, videoresult, userMessage, multimedia = []")
    chatList.scrollTop = chatList.scrollHeight;
    return
}


const showLoadingAnimation = (query_text) => {
    // bot 
    const html = `<div class="message-content">
        <img src="/static/image/gemini.svg" alt="Gemini Image" class="avatar">
        <p class="text"></p>
        <div class="loading-indicator">
           <div class="loading-bar"></div>
           <div class="loading-bar"></div>
           <div class="loading-bar"></div>
        </div>
        <div class="chattime">${String(Date().toLocaleString()).split(" ")[4].slice(0, -3)}</div> 
      </div>
      <span onclick="copyMessage(this)"  class="icon material-symbols-rounded">content_copy</span>`;

    const incomingMessageDiv = createMessageElement(html, "incoming", "loading");
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

    userdiv();

    typingForm.reset();
    chatList.scrollTo(0, chatList.scrollHeight);

    showLoadingAnimation(userMessage);
}

suggestions.forEach(suggestion => {
    suggestion.addEventListener("click", () => {
        userMessage = suggestion.querySelector(".usertext").innerText;
        handleOutgoingChat();
    });
});

// RecordRTC
let mediaRecorder;
let audioChunks = [];
let isRecording = false;  // 用来判断当前是否正在录音
// deleteChatButton.onclick = function() 


sttButton.onclick = async () => {    // STT  //sttButton.addEventListener("click", async () => {  

    if (!isRecording) {
        // 开始录音
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            sttButton.style.backgroundColor = "#f44336";
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); // 使用 webm 格式
                audioChunks = []; // 清空数据块

                // 将 Blob 转换为 Base64
                const reader = new FileReader();
                reader.onloadend = async () => {
                    const base64data = reader.result;

                    // 发送音频数据到后端
                    const response = await fetch('/stt', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ audioData: base64data })
                    });

                    const result = await response.json();
                    userMessage = result.message
                    console.log(result.message);

                    userdiv();

                    showLoadingAnimation(userMessage);
                    sttButton.style.backgroundColor = "#383838";
                };
                reader.readAsDataURL(audioBlob); // 转换为 Base64

                stream.getTracks().forEach(track => track.stop());

            };

            mediaRecorder.start();
            console.log("开始录音...");
            isRecording = true;
            sttButton.classList.add('recording'); // 添加正在录音的样式

        } catch (error) {
            console.error("无法获取音频流", error);
        }
    } else {
        // 停止录音
        mediaRecorder.stop();
        console.log("录音停止");
        isRecording = false;
    }
};



const getAndPlayAudioFromText = () => { }

deleteChatButton.onclick = function () {
    if (confirm("Are you sure you want to delete all messages?"))
        localStorage.removeItem("savedChats");
    loadLocalstorageData();
};


typingForm.addEventListener("submit", (e) => {
    e.preventDefault();

    handleOutgoingChat();
});

const fileInput = document.getElementById('file_upload');

uploadForm.onsubmit = (async (event) => {
    event.preventDefault(); // 阻止默認提交
    if (!fileInput.files.length) {
        alert("我入到黎 圖又冇? Link又冇?"); // 提示用户
        return;
    }
    userdiv();
    uploadModal.style.display = 'none'; // 隐藏弹窗
    uploadForm.reset();
});

fileInput.addEventListener('change', function () {
    console.log("inputed image")
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (evt) {
            videoresult = evt.target.result
            const result = evt.target.result;
            multimedia.push(evt.target.result);
            if (result && result.startsWith("data:video/")) {
                const videoURL = URL.createObjectURL(file); // 創建視頻的臨時 URL
                sessionStorage.setItem('image_data', videoURL); // 將 URL 存儲到 sessionStorage
                console.log("videoupload");
                return;
            }

            sessionStorage.setItem('image_data', evt.target.result)
            console.log("文件類型:", file.type);
            videoresult = null
        };
        reader.readAsDataURL(file); // 讀取文件
    }
});

const userdiv = () => {

    let imageData = sessionStorage.getItem("image_data");

    let content = "";
    let usertext = "";
    if (userMessage !== null) {
        usertext = `<p class="usertext">hello</p>`;
    } else if (videoresult !== null) {
        content = `<video controls style="max-width: 80%; max-height: 200px;"><source src="${imageData}" type="video/mp4"></video>`;
    } else {
        content = `<img src="${imageData}" style="max-width: 80%; max-height: 200px;">`;
    }

    const time = String(Date().toLocaleString()).split(" ")[4].slice(0, -3);
    const html = `<div class="message-content">
        <img src="/static/image/image.jpg" alt="User Image" class="avatar">
        ${content}
        ${usertext}
        <div class="time">${time}</div>
    </div>
    <script>chatbotimage.reset()</script>`;


    const outgoingMessageDiv = createMessageElement(html, "outgoing");
    console.log(userMessage);
    if (usertext != "") { outgoingMessageDiv.querySelector(".usertext").innerText = userMessage; }
    chatList.appendChild(outgoingMessageDiv);
    chatList.scrollTo(0, chatList.scrollHeight);
    document.body.classList.add("hide-header");

};

if (navigator.geolocation) {

    var options = {
        enableHighAccuracy: true,
        maximumAge: 30000,
        timeout: 27000
    };

    navigator.geolocation.getCurrentPosition(
        (position) => {
            latitude = position.coords.latitude;
            longitude = position.coords.longitude;
            console.log(latitude)
            getAddressFromCoordinates(latitude, longitude);
        },
        (error) => {
            handleLocationError(error);
        },
        options // 传入选项
    );

} else {
    alert("瀏覽器不支持地理定位。");
};



const getAddressFromCoordinates = async (lat, lng) => {
    // 使用 Google Maps Geocoding API

    const addressResponse = await fetch('/api/geocode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'latitude': lat,
            'longitude': lng
        })
    });

    const result = await addressResponse.json();
    addressoutput = result.localtion
    console.log(addressoutput)
    document.getElementById('address').innerHTML = `用戶位置: ${addressoutput}`
};


function handleLocationError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            document.getElementById('address').innerHTML = `用戶拒絕提供地理位置`;
            break;
        case error.POSITION_UNAVAILABLE:
            alert("位置信息不可用。");
            break;
        case error.TIMEOUT:
            alert("timeout。");
            break;
        case error.UNKNOWN_ERROR:
            alert("unknow error。");
            break;
    }
};