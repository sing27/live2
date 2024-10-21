// const cubism4Model = "./assets/kei_vowels_pro/kei_vowels_pro.model3.json";
// const cubism4Model = "./assets/Hiyori/Hiyori.model3.json";
// const cubism4Model = "./assets/March 7th/March 7th.model3.json";
const cubism4Model = "/static/assets/haru/haru_greeter_t03.model3.json";

let models = null;
let model4 = null;
// const models = await Promise.all([
//     live2d.Live2DModel.from(cubism4Model)
// ]);

const live2d = PIXI.live2d;

const loadModels = async () => {
    models = await Promise.all([
        live2d.Live2DModel.from(cubism4Model)
    ]);
    model4 = models[0];

    // const model4 = models[0];
}


(async function main() {
    await loadModels();
    const app = new PIXI.Application({
        view: document.getElementById("canvas"),
        autoStart: true,
        resizeTo: window,
        backgroundColor: 0xE4E4E4,
    });

    models.forEach((model) => {
        app.stage.addChild(model);

        const scaleX = (innerWidth) / model.width;
        const scaleY = (innerHeight) / model.height;

        // fit the window
        model.scale.set(Math.min(scaleX, scaleY));
        model.y = innerHeight * 0.1;
        // draggable(model);  // draggable a

        // 禁用拖动
        model.interactive = true;
        model.buttonMode = false;
        model.draggable = false;

        // 添加视线跟随鼠标事件
        model.on("pointerdown", (e) => {
            model._pointerX = e.data.global.x - model.x;
            model._pointerY = e.data.global.y - model.y;
        });
        model.on("pointermove", (e) => {
            if (model.dragging) {
                model.position.x = e.data.global.x - model._pointerX;
                model.position.y = e.data.global.y - model._pointerY;
            }
        });
        model.on("pointerupoutside", () => (model.dragging = false));
        model.on("pointerup", () => (model.dragging = false));

    });

    console.log(innerWidth)
    // model4.x = innerWidth / 2;
    // 居中显示
    model4.x = (innerWidth - model4.width) / 9;

    model4.on("hit", (hitAreas) => {
        if (hitAreas.includes("Body")) {
            model4.motion("Tap");
        }

        if (hitAreas.includes("Head")) {
            model4.expression();
        }
    });


    let audiotext = ""  // data:audio/mp3;base64,....

    $("#play").click(function () {
        // talk(model4, "/static/voice/01_kei_jp.wav");
        talk(model4, `data:audio/wav;base64,${audiotext}`)
    });

    $("#start").click(function () {
        console.log($("#text").val());
        let text = $("#text").val().trim();
        if (text == "") {
            alert("请输入内容");
            return false;
        }
        $("#start").prop("disabled", true);
        axios.get("http://127.0.0.1:2020/dealAudio?file_name=test.mp3&voice=xiaoxiao&text=" + text)
            .then(response => {
                console.log(response.data);
                const audioUrl = response.data + "?v=" + new Date().getTime();
                talk(model4, audioUrl);
                $("#start").prop("disabled", false);
            })
            .catch(error => {
                console.error('请求接口失败:', error);
                $("#start").prop("disabled", false);
            });
    });


})();


function talk(model, audio) {
    var audio_link = audio;  //[Optional arg, can be null or empty] [relative or full url path] [mp3 or wav file] "./Keira.wav"
    var volume = 1; // [Optional arg, can be null or empty] [0.0 - 1.0]
    var expression = 8; // [Optional arg, can be null or empty] [index|name of expression]
    var resetExpression = true; // [Optional arg, can be null or empty] [true|false] [default: true] [if true, expression will be reset to default after animation is over]
    var crossOrigin = "anonymous"; // [Optional arg, to use not same-origin audios] [DEFAULT: null]

    model.speak(audio_link, {
        volume: volume,
        expression: expression,
        resetExpression: resetExpression,
        crossOrigin: crossOrigin
    })
    model.speak(audio_link)
    model.speak(audio_link, { volume: volume })
    model.speak(audio_link, { expression: expression, resetExpression: resetExpression })

}
