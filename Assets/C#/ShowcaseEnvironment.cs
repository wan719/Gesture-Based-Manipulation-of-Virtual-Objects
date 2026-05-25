using UnityEngine;

public class ShowcaseEnvironment : MonoBehaviour
{
    public bool createGround = true;
    public bool tuneLighting = true;
    public Color groundColor = new Color(0.04f, 0.11f, 0.13f, 1f);
    public Color ambientColor = new Color(0.45f, 0.62f, 0.7f, 1f);
    public float ambientIntensity = 1.35f;
    public float directionalLightIntensity = 1.8f;

    private void Start()
    {
        if (createGround && GameObject.Find("ShowcaseGround") == null)
        {
            CreateGround();
        }

        if (tuneLighting)
        {
            TuneLighting();
        }
    }

    private void CreateGround()
    {
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "ShowcaseGround";
        ground.transform.position = Vector3.zero;
        ground.transform.localScale = new Vector3(3f, 1f, 3f);

        Renderer renderer = ground.GetComponent<Renderer>();
        Shader shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null)
        {
            shader = Shader.Find("Standard");
        }

        if (renderer != null && shader != null)
        {
            Material material = new Material(shader);
            material.color = groundColor;
            material.SetFloat("_Metallic", 0f);
            material.SetFloat("_Glossiness", 0.25f);
            renderer.material = material;
        }
    }

    private void TuneLighting()
    {
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
        RenderSettings.ambientLight = ambientColor * ambientIntensity;

        Light directionalLight = FindObjectOfType<Light>();
        if (directionalLight == null || directionalLight.type != LightType.Directional)
        {
            GameObject lightObject = new GameObject("ShowcaseDirectionalLight");
            directionalLight = lightObject.AddComponent<Light>();
            directionalLight.type = LightType.Directional;
            lightObject.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
        }

        directionalLight.intensity = directionalLightIntensity;
    }
}
