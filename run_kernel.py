import json

def load_json(path):
    with open(path) as f:
        return json.load(f)

def main():
    kernel = load_json("kernel/thalean_kernel.v1.json")
    spec = load_json(kernel["inputs"]["spec"])

    print("KERNEL:", kernel["kernel_id"])
    print("GRAPH:", kernel["graph_id"])
    print("VERTICES:", spec.get("vertices"))

if __name__ == "__main__":
    main()
