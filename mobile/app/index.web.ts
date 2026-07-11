import { registerRootComponent } from 'expo';
import { LoadSkiaWeb } from '@shopify/react-native-skia/lib/module/web';

async function start(): Promise<void> {
  await LoadSkiaWeb({ locateFile: () => '/canvaskit.wasm' });
  const { default: App } = await import('./App');
  registerRootComponent(App);
}

void start();
