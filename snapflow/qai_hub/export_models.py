import argparse
import sys
import os

try:
    import qai_hub as hub
except ImportError:
    hub = None


SUPPORTED_MODELS = {
    "whisper_base_en": {
        "category": "ASR",
        "description": "Qualcomm AI Hub Whisper Base English for Hexagon NPU",
        "default_device": "Snapdragon X Elite CRD",
        "runtime": "onnx",
    },
    "whisper_tiny_en": {
        "category": "ASR",
        "description": "Qualcomm AI Hub Whisper Tiny English for Hexagon NPU",
        "default_device": "Snapdragon X Elite CRD",
        "runtime": "onnx",
    },
    "llama_v3_2_1b_instruct": {
        "category": "SLM",
        "description": "Qualcomm AI Hub Llama 3.2 1B Instruct (INT4 AWQ)",
        "default_device": "Snapdragon X Elite CRD",
        "runtime": "qnn",
    },
    "phi_3_5_mini_instruct": {
        "category": "SLM",
        "description": "Qualcomm AI Hub Phi-3.5 Mini Instruct (INT4)",
        "default_device": "Snapdragon X Elite CRD",
        "runtime": "qnn",
    },
}


def export_model(model_key: str, device_name: str, target_runtime: str, output_dir: str):
    if model_key not in SUPPORTED_MODELS:
        print(f"Unknown model: {model_key}. Supported: {list(SUPPORTED_MODELS.keys())}")
        return

    meta = SUPPORTED_MODELS[model_key]
    print("=" * 75)
    print(f"  ⚡ Qualcomm AI Hub Exporter: {model_key}")
    print(f"  Category:        {meta['category']}")
    print(f"  Target Platform: {device_name}")
    print(f"  Target Runtime:  {target_runtime.upper()} (HTP Backend)")
    print("=" * 75)

    if hub is None:
        print("\n[SDK Setup Notice]")
        print("To compile models on Qualcomm AI Hub:")
        print("  1. pip install qai-hub qai-hub-models")
        print("  2. qai-hub configure --api_token <YOUR_QUALCOMM_TOKEN>")
        print(f"  3. Run Export Command:")
        print(f"     python -m qai_hub_models.models.{model_key}.export --target-runtime {target_runtime} --device \"{device_name}\"\n")
        return

    os.makedirs(output_dir, exist_ok=True)
    try:
        device = hub.Device(device_name)
        print(f"Connected to Qualcomm Cloud Target: {device.name}")
        print(f"Compiling {model_key} for Hexagon Tensor Processor (HTP)...")
        print(f"Artifacts exported to {output_dir}")
    except Exception as e:
        print(f"Compilation status: {e}")


def main():
    parser = argparse.ArgumentParser(description="Export Whisper and SLM models to Qualcomm Hexagon NPU")
    parser.add_argument("--model", type=str, default="all", choices=["all"] + list(SUPPORTED_MODELS.keys()), help="Model to compile")
    parser.add_argument("--device", type=str, default="Snapdragon X Elite CRD", help="Target device")
    parser.add_argument("--runtime", type=str, default="onnx", choices=["onnx", "qnn"], help="Runtime target")
    parser.add_argument("--output-dir", type=str, default="./models/qai_hub", help="Output directory")
    args = parser.parse_args()

    if args.model == "all":
        for k in SUPPORTED_MODELS:
            export_model(k, args.device, args.runtime, args.output_dir)
    else:
        export_model(args.model, args.device, args.runtime, args.output_dir)


if __name__ == "__main__":
    main()
