import { ButtonController } from './core/button-controller.js';

const cameraController = new ButtonController({
  selector: 'button[data-is-muted]',
  iconNames: ['videocam', 'videocam_off'],
  keywords: ['fotocamera', 'videocamera', 'camera', 'videocam', 'cam'],   // fallback legacy
});

export const getCameraState = () => cameraController.getState();
export const toggleCamera = () => cameraController.toggle();
