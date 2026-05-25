using UnityEngine;

public class ShowcaseCamera : MonoBehaviour
{
    public Transform target;
    public float distance = 4.2f;
    public float height = 1.35f;
    public float angle = 18f;
    public float followSmooth = 5f;
    public Vector3 lookOffset = new Vector3(0f, 0.45f, 0f);

    private void Start()
    {
        if (target == null)
        {
            GameObject robotDog = GameObject.Find("RobotDog");
            if (robotDog != null)
            {
                target = robotDog.transform;
            }
        }
    }

    private void LateUpdate()
    {
        if (target == null)
        {
            return;
        }

        Quaternion orbitRotation = Quaternion.Euler(angle, target.eulerAngles.y, 0f);
        Vector3 desiredPosition = target.position - orbitRotation * Vector3.forward * distance + Vector3.up * height;
        transform.position = Vector3.Lerp(transform.position, desiredPosition, followSmooth * Time.deltaTime);

        Vector3 lookPoint = target.position + lookOffset;
        Quaternion desiredRotation = Quaternion.LookRotation(lookPoint - transform.position, Vector3.up);
        transform.rotation = Quaternion.Slerp(transform.rotation, desiredRotation, followSmooth * Time.deltaTime);
    }
}
