using System.Collections.Generic;
using UnityEngine;

public class DogController : MonoBehaviour
{
    private const string ActionIdle = "idle";
    private const string ActionForward = "forward";
    private const string ActionBackward = "backward";
    private const string ActionSit = "sit";
    private const string ActionWave = "wave";

    [Header("Leg Bones")]
    public Transform frontLeftUpperLeg;
    public Transform frontRightUpperLeg;
    public Transform rearLeftUpperLeg;
    public Transform rearRightUpperLeg;
    public Transform frontLeftLowerLeg;
    public Transform frontRightLowerLeg;
    public Transform rearLeftLowerLeg;
    public Transform rearRightLowerLeg;
    public Transform wavePart;

    [Header("Move")]
    public float moveSpeed = 0.8f;
    public float moveSmooth = 5f;

    [Header("Body")]
    public float idleBreathAmplitude = 0.008f;
    public float idleBreathFrequency = 1.2f;
    public float moveBounceAmplitude = 0.025f;
    public float moveBounceFrequency = 5.5f;
    public float bodyPitchAmplitude = 2.5f;
    public float bodyRollAmplitude = 2.0f;

    [Header("Gait")]
    public float legSwingAmplitude = 18f;
    public float lowerLegBendAmplitude = 14f;
    public float legSwingFrequency = 5.5f;
    public float legLerpSpeed = 9f;

    [Header("Sit")]
    public float sitHeightOffset = 0.20f;
    public float sitUpperLegAngle = 18f;
    public float sitLowerLegAngle = -20f;
    public float heightSmoothSpeed = 6f;

    [Header("Wave")]
    public float waveUpperLegLiftAngle = -25f;
    public float waveLowerLegSwingAngle = 25f;
    public float waveFrequency = 3.0f;
    public float waveBodyYawAmplitude = 3f;

    [Header("Transition")]
    public float actionTransitionSpeed = 8f;

    private readonly Dictionary<Transform, Quaternion> initialRotations = new Dictionary<Transform, Quaternion>();
    private Vector3 bodyBaseLocalPosition;
    private Quaternion bodyBaseLocalRotation;
    private string currentAction = ActionIdle;
    private string requestedAction = ActionIdle;
    private float currentMoveVelocity;
    private float targetBodyHeightOffset;
    private float currentBodyHeightOffset;
    private float actionTime;

    private void Awake()
    {
        bodyBaseLocalPosition = transform.localPosition;
        bodyBaseLocalRotation = transform.localRotation;
        AutoBindBones();
        CacheInitialRotations();
    }

    private void Update()
    {
        float deltaTime = Time.deltaTime;
        actionTime += deltaTime;

        if (currentAction != requestedAction)
        {
            currentAction = requestedAction;
            actionTime = 0f;
        }

        float targetMoveVelocity = GetTargetMoveVelocity();
        currentMoveVelocity = Mathf.Lerp(currentMoveVelocity, targetMoveVelocity, moveSmooth * deltaTime);

        if (Mathf.Abs(currentMoveVelocity) > 0.001f)
        {
            bodyBaseLocalPosition += Vector3.forward * currentMoveVelocity * deltaTime;
        }

        switch (currentAction)
        {
            case ActionForward:
                AnimateMove(1f);
                break;
            case ActionBackward:
                AnimateMove(-1f);
                break;
            case ActionSit:
                AnimateSit();
                break;
            case ActionWave:
                AnimateWave();
                break;
            default:
                AnimateIdle();
                break;
        }
    }

    public void SetAction(string action)
    {
        string normalizedAction = string.IsNullOrWhiteSpace(action)
            ? ActionIdle
            : action.Trim().ToLowerInvariant();

        if (!IsKnownAction(normalizedAction))
        {
            Debug.LogWarning($"DogController received unknown action: {action}. Falling back to idle.");
            normalizedAction = ActionIdle;
        }

        requestedAction = normalizedAction;
    }

    private void AnimateIdle()
    {
        float breath = Mathf.Sin(Time.time * idleBreathFrequency * Mathf.PI * 2f) * idleBreathAmplitude;
        targetBodyHeightOffset = breath;
        ApplyBodyPose(targetBodyHeightOffset, 0f, 0f, 0f);
        RestoreAllLegs();
    }

    private void AnimateMove(float direction)
    {
        float phase = Time.time * legSwingFrequency * Mathf.PI * 2f;
        float bounce = Mathf.Abs(Mathf.Sin(phase)) * moveBounceAmplitude;
        float pitch = Mathf.Sin(phase) * bodyPitchAmplitude * direction;
        float roll = Mathf.Cos(phase) * bodyRollAmplitude;

        targetBodyHeightOffset = bounce;
        ApplyBodyPose(targetBodyHeightOffset, pitch, 0f, roll);

        float groupA = Mathf.Sin(phase) * legSwingAmplitude * direction;
        float groupB = Mathf.Sin(phase + Mathf.PI) * legSwingAmplitude * direction;
        float bendA = Mathf.Abs(Mathf.Sin(phase)) * lowerLegBendAmplitude;
        float bendB = Mathf.Abs(Mathf.Sin(phase + Mathf.PI)) * lowerLegBendAmplitude;

        ApplyLegPose(frontLeftUpperLeg, frontLeftLowerLeg, groupA, -bendA);
        ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, groupA, -bendA);
        ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, groupB, -bendB);
        ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, groupB, -bendB);
    }

    private void AnimateSit()
    {
        targetBodyHeightOffset = -Mathf.Abs(sitHeightOffset);
        ApplyBodyPose(targetBodyHeightOffset, -3f, 0f, 0f);

        ApplyLegPose(frontLeftUpperLeg, frontLeftLowerLeg, sitUpperLegAngle, sitLowerLegAngle);
        ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, sitUpperLegAngle, sitLowerLegAngle);
        ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, -sitUpperLegAngle, -sitLowerLegAngle);
        ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, -sitUpperLegAngle, -sitLowerLegAngle);
    }

    private void AnimateWave()
    {
        float phase = Time.time * waveFrequency * Mathf.PI * 2f;
        float yaw = Mathf.Sin(phase * 0.5f) * waveBodyYawAmplitude;
        float roll = Mathf.Sin(phase * 0.5f) * bodyRollAmplitude * 0.6f;
        float lowerSwing = Mathf.Sin(phase) * waveLowerLegSwingAngle;

        targetBodyHeightOffset = idleBreathAmplitude * 0.5f;
        ApplyBodyPose(targetBodyHeightOffset, 0f, yaw, roll);

        ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, 4f, -6f);
        ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, -4f, 6f);
        ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, -4f, 6f);

        Transform wavingPart = wavePart != null ? wavePart : frontLeftLowerLeg;
        ApplyLegPose(frontLeftUpperLeg, null, waveUpperLegLiftAngle, 0f);

        if (wavingPart != null && initialRotations.TryGetValue(wavingPart, out Quaternion initialRotation))
        {
            Quaternion targetRotation = initialRotation * Quaternion.Euler(0f, 0f, lowerSwing);
            LerpLocalRotation(wavingPart, targetRotation);
        }
    }

    private void ApplyBodyPose(float heightOffset, float pitch, float yaw, float roll)
    {
        float deltaTime = Time.deltaTime;
        currentBodyHeightOffset = Mathf.Lerp(currentBodyHeightOffset, heightOffset, heightSmoothSpeed * deltaTime);
        Vector3 targetPosition = bodyBaseLocalPosition + Vector3.up * currentBodyHeightOffset;
        Quaternion targetRotation = bodyBaseLocalRotation * Quaternion.Euler(pitch, yaw, roll);

        transform.localPosition = Vector3.Lerp(transform.localPosition, targetPosition, actionTransitionSpeed * deltaTime);
        transform.localRotation = Quaternion.Slerp(transform.localRotation, targetRotation, actionTransitionSpeed * deltaTime);
    }

    private void ApplyLegPose(Transform upperLeg, Transform lowerLeg, float upperAngle, float lowerAngle)
    {
        if (upperLeg != null && initialRotations.TryGetValue(upperLeg, out Quaternion upperInitialRotation))
        {
            Quaternion upperTarget = upperInitialRotation * Quaternion.Euler(upperAngle, 0f, 0f);
            LerpLocalRotation(upperLeg, upperTarget);
        }

        if (lowerLeg != null && initialRotations.TryGetValue(lowerLeg, out Quaternion lowerInitialRotation))
        {
            Quaternion lowerTarget = lowerInitialRotation * Quaternion.Euler(lowerAngle, 0f, 0f);
            LerpLocalRotation(lowerLeg, lowerTarget);
        }
    }

    private void RestoreAllLegs()
    {
        RestoreLeg(frontLeftUpperLeg);
        RestoreLeg(frontRightUpperLeg);
        RestoreLeg(rearLeftUpperLeg);
        RestoreLeg(rearRightUpperLeg);
        RestoreLeg(frontLeftLowerLeg);
        RestoreLeg(frontRightLowerLeg);
        RestoreLeg(rearLeftLowerLeg);
        RestoreLeg(rearRightLowerLeg);

        if (wavePart != null)
        {
            RestoreLeg(wavePart);
        }
    }

    private void RestoreLeg(Transform leg)
    {
        if (leg != null && initialRotations.TryGetValue(leg, out Quaternion initialRotation))
        {
            LerpLocalRotation(leg, initialRotation);
        }
    }

    private void LerpLocalRotation(Transform target, Quaternion targetRotation)
    {
        target.localRotation = Quaternion.Slerp(
            target.localRotation,
            targetRotation,
            legLerpSpeed * Time.deltaTime
        );
    }

    private float GetTargetMoveVelocity()
    {
        if (currentAction == ActionForward)
        {
            return moveSpeed;
        }

        if (currentAction == ActionBackward)
        {
            return -moveSpeed;
        }

        return 0f;
    }

    private bool IsKnownAction(string action)
    {
        return action == ActionIdle
            || action == ActionForward
            || action == ActionBackward
            || action == ActionSit
            || action == ActionWave;
    }

    private void AutoBindBones()
    {
        frontLeftUpperLeg = frontLeftUpperLeg != null ? frontLeftUpperLeg : FindDeepChild(transform, "spot_upperLeg_FL");
        frontRightUpperLeg = frontRightUpperLeg != null ? frontRightUpperLeg : FindDeepChild(transform, "spot_upperLeg_FR");
        rearLeftUpperLeg = rearLeftUpperLeg != null ? rearLeftUpperLeg : FindDeepChild(transform, "spot_upperLeg_RL");
        rearRightUpperLeg = rearRightUpperLeg != null ? rearRightUpperLeg : FindDeepChild(transform, "spot_upperLeg_RR");
        frontLeftLowerLeg = frontLeftLowerLeg != null ? frontLeftLowerLeg : FindDeepChild(transform, "spot_lowerLeg_FL");
        frontRightLowerLeg = frontRightLowerLeg != null ? frontRightLowerLeg : FindDeepChild(transform, "spot_lowerLeg_FR");
        rearLeftLowerLeg = rearLeftLowerLeg != null ? rearLeftLowerLeg : FindDeepChild(transform, "spot_lowerLeg_RL");
        rearRightLowerLeg = rearRightLowerLeg != null ? rearRightLowerLeg : FindDeepChild(transform, "spot_lowerLeg_RR");

        if (wavePart == null)
        {
            wavePart = frontLeftLowerLeg != null ? frontLeftLowerLeg : FindDeepChild(transform, "spot_legTarget_FL");
        }

        WarnIfMissing(frontLeftUpperLeg, "spot_upperLeg_FL");
        WarnIfMissing(frontRightUpperLeg, "spot_upperLeg_FR");
        WarnIfMissing(rearLeftUpperLeg, "spot_upperLeg_RL");
        WarnIfMissing(rearRightUpperLeg, "spot_upperLeg_RR");
        WarnIfMissing(frontLeftLowerLeg, "spot_lowerLeg_FL");
        WarnIfMissing(frontRightLowerLeg, "spot_lowerLeg_FR");
        WarnIfMissing(rearLeftLowerLeg, "spot_lowerLeg_RL");
        WarnIfMissing(rearRightLowerLeg, "spot_lowerLeg_RR");
    }

    private void CacheInitialRotations()
    {
        CacheInitialRotation(frontLeftUpperLeg);
        CacheInitialRotation(frontRightUpperLeg);
        CacheInitialRotation(rearLeftUpperLeg);
        CacheInitialRotation(rearRightUpperLeg);
        CacheInitialRotation(frontLeftLowerLeg);
        CacheInitialRotation(frontRightLowerLeg);
        CacheInitialRotation(rearLeftLowerLeg);
        CacheInitialRotation(rearRightLowerLeg);
        CacheInitialRotation(wavePart);
    }

    private void CacheInitialRotation(Transform target)
    {
        if (target != null && !initialRotations.ContainsKey(target))
        {
            initialRotations.Add(target, target.localRotation);
        }
    }

    private void WarnIfMissing(Transform target, string boneName)
    {
        if (target == null)
        {
            Debug.LogWarning($"DogController could not find bone: {boneName}. Bind it in the Inspector if this part should animate.");
        }
    }

    private Transform FindDeepChild(Transform parent, string childName)
    {
        if (parent == null)
        {
            return null;
        }

        foreach (Transform child in parent)
        {
            if (child.name == childName)
            {
                return child;
            }

            Transform result = FindDeepChild(child, childName);
            if (result != null)
            {
                return result;
            }
        }

        return null;
    }
}
