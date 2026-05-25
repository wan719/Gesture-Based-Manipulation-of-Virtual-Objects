using UnityEngine;

public class DogKeyboardTest : MonoBehaviour
{
    public DogController dogController;

    private void Start()
    {
        if (dogController == null)
        {
            dogController = GetComponent<DogController>();
        }
    }

    private void Update()
    {
        if (dogController == null)
        {
            return;
        }

        if (Input.GetKeyDown(KeyCode.Alpha1) || Input.GetKeyDown(KeyCode.I))
        {
            dogController.SetAction("idle");
        }
        else if (Input.GetKeyDown(KeyCode.Alpha2) || Input.GetKeyDown(KeyCode.F))
        {
            dogController.SetAction("forward");
        }
        else if (Input.GetKeyDown(KeyCode.Alpha3) || Input.GetKeyDown(KeyCode.B))
        {
            dogController.SetAction("backward");
        }
        else if (Input.GetKeyDown(KeyCode.Alpha4) || Input.GetKeyDown(KeyCode.S))
        {
            dogController.SetAction("sit");
        }
        else if (Input.GetKeyDown(KeyCode.Alpha5) || Input.GetKeyDown(KeyCode.W))
        {
            dogController.SetAction("wave");
        }
    }
}
