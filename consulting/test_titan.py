import json
import sys

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("[ERROR] 'boto3' no está instalado en este entorno.")
    print("Instalalo ejecutando: pip install boto3")
    sys.exit(1)

REGIONS_TO_TEST = ["us-east-1", "us-east-2"]
MODELS_TO_TEST = [
    "amazon.titan-embed-text-v2:0",
    "amazon.titan-embed-text-v1",
]

TEST_PROMPT = "Prueba de generación de embeddings para EDET Argentina"


def test_titan():
    print("=" * 65)
    print(" Verificando disponibilidad de Amazon Titan Embeddings en AWS Bedrock")
    print("=" * 65)

    any_success = False

    for region in REGIONS_TO_TEST:
        print(f"\n[*] Probando en región: {region} ...")
        
        # 1. Intentar listar modelos habilitados
        try:
            bedrock_ctrl = boto3.client("bedrock", region_name=region)
            resp = bedrock_ctrl.list_foundation_models(byOutputModality="EMBEDDING")
            models_in_region = [m["modelId"] for m in resp.get("modelSummaries", []) if "titan" in m.get("modelId", "").lower()]
            print(f"    - Modelos Titan encontrados en catálogo: {models_in_region}")
        except ClientError as e:
            print(f"    - No se pudo listar catálogo (permisos IAM/SCP): {e.response['Error']['Code']}")
        except Exception as e:
            print(f"    - Error conectando a Bedrock Control: {e}")

        # 2. Intentar invocar los modelos de embedding
        try:
            bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
        except Exception as e:
            print(f"    [!] Error creando cliente bedrock-runtime: {e}")
            continue

        for model_id in MODELS_TO_TEST:
            print(f"\n    -> Intentando invocar '{model_id}'...")
            body = json.dumps({"inputText": TEST_PROMPT})
            
            try:
                response = bedrock_runtime.invoke_model(
                    modelId=model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=body,
                )
                
                response_body = json.loads(response["body"].read())
                embedding = response_body.get("embedding", [])
                
                print(f"       ✅ ¡ÉXITO! Modelo '{model_id}' disponible y funcionando.")
                print(f"       📊 Dimensión del vector generado: {len(embedding)}")
                print(f"       🔍 Primeros 3 valores: {embedding[:3]}")
                any_success = True
                break
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")
                error_msg = e.response.get("Error", {}).get("Message", str(e))
                print(f"       ❌ DENEGADO / NO DISPONIBLE:")
                print(f"          Código: {error_code}")
                print(f"          Mensaje: {error_msg}")
            except Exception as e:
                print(f"       ❌ Error inesperado: {type(e).__name__} - {e}")

        if any_success:
            break

    print("\n" + "=" * 65)
    if any_success:
        print(" 🎉 CONCLUSIÓN: Tenés Titan habilitado y listo para usar.")
    else:
        print(" ⚠️ CONCLUSIÓN: Titan NO está habilitado en tu cuenta AWS.")
        print("    (Típicamente requiere habilitar 'Model access' en la consola de AWS Bedrock,")
        print("     o una política SCP está bloqueando el InvokeModel en esa región).")
    print("=" * 65)


if __name__ == "__main__":
    test_titan()

