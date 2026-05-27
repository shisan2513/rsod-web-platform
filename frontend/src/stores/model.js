import { defineStore } from "pinia";
import { ref } from "vue";

export const useModelStore = defineStore("model", () => {
  const currentModel = ref("yolo11n");

  const setModel = (model) => {
    currentModel.value = model;
  };

  return { currentModel, setModel };
});
