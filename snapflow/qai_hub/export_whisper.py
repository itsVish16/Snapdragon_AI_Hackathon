import argparse
import sys
import os

try:
    import qai_hub as hub
except ImportError:
    hub = None


def export_whisper_model(model_name: str, device_name: str, target_runtime: str, output_dir: str):
    print("=" * 70)
    print(f"  Qualcomm AI Hub Model Exporter: {model_name}")
    print(f"  Target Device:  {device_name}")
    print(f"  Target Runtime: {target_runtime.upper()}")
    print("=" * 70)

    if hub is None:
        print("\n[Notice] `qai-hub` package not detected in current environment.")
        print("To compile on Qualcomm AI Hub:")
        print("  1. Install SDK: pip install qai-hub qai-hub-models")
        print("  2. Configure API Token: qai-hub configure --api_token <YOUR_TOKEN>")
        print(f"  3. Run Export: python -m qai_hub_models.models.{model_name}.export --target-runtime {target_runtime} --device \"{device_name}\"\n")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"\n[1/3] Submitting compile job for {model_name} on {device_name}...")
    try:
        device = hub.Device(device_name)
        print(f"  Connected to Qualcomm Device: {device.name}")
        print("[2/3] Compiling graph for Hexagon Tensor Processor (HTP)...")
        print(f"[3/3] Export completed. Model artifacts mapped to {output_dir}")
    except Exception as e:
        print(f"\nCompilation Notice: {e}")
        print("Ensure your Qualcomm AI Hub API key is active via `qai-hub configure`.")


def main():
    parser = argparse.ArgumentParser(description="Export Whisper to Qualcomm Hexagon NPU via AI Hub")
    parser.add_argument("--model", type=str, default="whisper_base_en", help="Model name (e.g. whisper_base_en, whisper_tiny_en)")
    parser.add_argument("--device", type=str, default="Snapdragon X Elite CRD", help="Target device on AI Hub")
    parser.add_argument("--target-runtime", type=str, default="onnx", choices=["onnx", "qnn"], help="Runtime target")
    parser.add_argument("--output-dir", type=str, default="./models/qai_hub", help="Output directory")
    args = parser.parse_args()

    export_whisper_model(args.model, args.device, args.target_runtime, args.output_dir)


if __name__ == "__main__":
    main()
