import { app } from "../../../python/Lib/site-packages/comfyui_frontend_package/static/scripts/app.js";

app.registerExtension({
    name: "ComfyUI.PromptComposer",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "PromptComposer") {
            // 确保节点每次都会重新执行
            nodeType.prototype.onExecuted = function(message) {
                this.isExecuted = false;
            };
        }
    },
});