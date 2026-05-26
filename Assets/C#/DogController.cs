using System.Collections.Generic;
using UnityEngine;

public class DogController : MonoBehaviour
{
    private const string ActionIdle = "idle";
    private const string ActionForward = "forward";
    private const string ActionBackward = "backward";
    private const string ActionSit = "sit";
    private const string ActionWave = "wave";
    private const string ActionJump = "jump";
    private const string ActionStand = "stand";
    private const string ActionRecover = "__recover";

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
    public float moveSpeed = 0.26f;
    public float moveSmooth = 2.8f;
    public float turnSpeed = 65f;
    public float turnSmooth = 6f;

    [Header("Body")]
    public float idleBreathAmplitude = 0.014f;
    public float idleBreathFrequency = 1.2f;
    public float idleSwayAmplitude = 1.1f;
    public float moveBounceAmplitude = 0.018f;
    public float moveBounceFrequency = 1.65f;
    public float bodyPitchAmplitude = 1.2f;
    public float bodyRollAmplitude = 1.1f;

    [Header("Gait")]
    public float legSwingAmplitude = 8f;
    public float lowerLegBendAmplitude = 5f;
    public float stepLiftAmplitude = 2.5f;
    public float legSwingFrequency = 1.65f;
    public float legLerpSpeed = 6f;

    [Header("Sit")]
    public float sitHeightOffset = 0.10f;
    public float sitUpperLegAngle = 12f;
    public float sitLowerLegAngle = -12f;
    public float heightSmoothSpeed = 6f;

    [Header("Stand")]
    public float standUpperLegAngle = 0f;
    public float standLowerLegAngle = 0f;
    public float standBodyLift = 0.50f;
    public float standBodyPitch = -25f;
    public float standFrontLegRaiseAngle = -48f;
    public float standFrontLowerLegAngle = -8f;
    public float standRearSupportUpperAngle = 14f;
    public float standRearSupportLowerAngle = 2f;
    public float standRecoverDuration = 0.75f;
    public float poseBlendSpeed = 6f;

    [Header("Wave")]
    public float waveUpperLegLiftAngle = -34f;
    public float waveLowerLegSwingAngle = 28f;
    public float waveFrequency = 1.45f;
    public float waveBodyYawAmplitude = 2.8f;

    [Header("Jump")]
    public float jumpHeight = 0.58f;
    public float jumpDuration = 0.92f;
    public float jumpLegTuckAngle = 34f;
    public float jumpSquashHeight = 0.05f;
    public float jumpBodyPitch = 4f;

    [Header("Transition")]
    public float actionTransitionSpeed = 5.5f;

    private readonly Dictionary<Transform, Quaternion> initialRotations = new Dictionary<Transform, Quaternion>();
    private Vector3 bodyBaseLocalPosition;
    private Quaternion bodyBaseLocalRotation;
    private string currentAction = ActionIdle;
    private string requestedAction = ActionIdle;
    private string pendingActionAfterRecover = ActionIdle;
    private float currentMoveVelocity;
    private float currentTurnVelocity;
    private float targetTurnDirection;
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

        float targetTurnVelocity = GetTargetTurnVelocity();
        currentTurnVelocity = Mathf.Lerp(currentTurnVelocity, targetTurnVelocity, turnSmooth * deltaTime);
        if (Mathf.Abs(currentTurnVelocity) > 0.01f)
        {
            bodyBaseLocalRotation *= Quaternion.Euler(0f, currentTurnVelocity * deltaTime, 0f);
        }

        if (Mathf.Abs(currentMoveVelocity) > 0.001f)
        {
            bodyBaseLocalPosition += bodyBaseLocalRotation * Vector3.forward * currentMoveVelocity * deltaTime;
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
            case ActionJump:
                AnimateJump();
                break;
            case ActionStand:
                AnimateStand();
                break;
            case ActionRecover:
                AnimateRecoverFromStand();
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

        if (
            normalizedAction != ActionStand
            && (currentAction == ActionStand || requestedAction == ActionStand)
        )
        {
            pendingActionAfterRecover = normalizedAction;
            requestedAction = ActionRecover;
            actionTime = 0f;
            return;
        }

        if (requestedAction == normalizedAction && currentAction == normalizedAction)
        {
            actionTime = 0f;
        }

        requestedAction = normalizedAction;
    }

    public void SetTurn(string turnCommand)
    {
        string normalizedTurn = string.IsNullOrWhiteSpace(turnCommand)
            ? "stop"
            : turnCommand.Trim().ToLowerInvariant();

        switch (normalizedTurn)
        {
            case "left":
            case "turn_left":
                targetTurnDirection = -1f;
                break;
            case "right":
            case "turn_right":
                targetTurnDirection = 1f;
                break;
            case "stop":
            case "none":
            case "straight":
                targetTurnDirection = 0f;
                break;
            default:
                Debug.LogWarning($"DogController received unknown turn command: {turnCommand}. Stopping turn.");
                targetTurnDirection = 0f;
                break;
        }
    }

    private void AnimateIdle()
    {
        float phase = Time.time * idleBreathFrequency * Mathf.PI * 2f;
        float breath = Mathf.Sin(phase) * idleBreathAmplitude;
        float yaw = Mathf.Sin(phase * 0.5f) * idleSwayAmplitude;
        float roll = Mathf.Cos(phase * 0.5f) * idleSwayAmplitude * 0.45f;

        ApplyBodyPose(breath, 0f, yaw, roll);
        ApplyNeutralLegPose();
    }

    private void AnimateStand()
    {
        float standBlend = Mathf.Clamp01(actionTime / 0.65f);
        float standPitch = Mathf.Lerp(0f, standBodyPitch, standBlend);
        float frontUpper = Mathf.Lerp(standUpperLegAngle, standFrontLegRaiseAngle, standBlend);
        float frontLower = Mathf.Lerp(standLowerLegAngle, standFrontLowerLegAngle, standBlend);
        float rearUpper = Mathf.Lerp(standUpperLegAngle, standRearSupportUpperAngle, standBlend);
        float rearLower = Mathf.Lerp(standLowerLegAngle, standRearSupportLowerAngle, standBlend);

        ApplyBodyPose(standBodyLift, standPitch, 0f, 0f);
        ApplyLegPose(frontLeftUpperLeg, frontLeftLowerLeg, frontUpper, frontLower);
        ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, frontUpper, frontLower);
        ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, rearUpper, rearLower);
        ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, rearUpper, rearLower);
        RestoreWavePartIfSeparate();
    }

    private void AnimateRecoverFromStand()
    {
        ApplyBodyPose(0f, 0f, 0f, 0f);
        ApplyNeutralLegPose();

        if (actionTime >= standRecoverDuration)
        {
            requestedAction = pendingActionAfterRecover;
        }
    }

    private void AnimateMove(float direction)
    {
        float effectiveFrequency = Mathf.Min(legSwingFrequency, 1.8f);
        float phase = actionTime * effectiveFrequency * Mathf.PI * 2f;
        float bounce = Mathf.Abs(Mathf.Sin(phase)) * Mathf.Min(moveBounceAmplitude, 0.02f);
        float pitch = Mathf.Sin(phase) * bodyPitchAmplitude * direction;
        float roll = Mathf.Cos(phase) * bodyRollAmplitude;

        ApplyBodyPose(bounce, pitch, 0f, roll);

        ApplyDiagonalStep(frontLeftUpperLeg, frontLeftLowerLeg, rearRightUpperLeg, rearRightLowerLeg, phase, direction);
        ApplyDiagonalStep(frontRightUpperLeg, frontRightLowerLeg, rearLeftUpperLeg, rearLeftLowerLeg, phase + Mathf.PI, direction);
        RestoreWavePartIfSeparate();
    }

    private void AnimateSit()
    {
        float sitDepth = Mathf.Min(Mathf.Abs(sitHeightOffset), 0.12f);
        float frontUpper = Mathf.Min(Mathf.Abs(sitUpperLegAngle), 14f);
        float frontLower = -Mathf.Min(Mathf.Abs(sitLowerLegAngle), 14f);
        float rearUpper = -frontUpper * 0.55f;
        float rearLower = Mathf.Abs(frontLower) * 0.55f;

        ApplyBodyPose(-sitDepth, -2f, 0f, 0f);

        ApplyLegPose(frontLeftUpperLeg, frontLeftLowerLeg, frontUpper, frontLower);
        ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, frontUpper, frontLower);
        ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, rearUpper, rearLower);
        ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, rearUpper, rearLower);
        RestoreWavePartIfSeparate();
    }

    private void AnimateWave()
    {
        float effectiveFrequency = Mathf.Min(waveFrequency, 1.55f);
        float phase = Time.time * effectiveFrequency * Mathf.PI * 2f;
        float yaw = Mathf.Sin(phase * 0.5f) * waveBodyYawAmplitude;
        float roll = Mathf.Sin(phase * 0.5f) * bodyRollAmplitude * 0.75f;
        float upperLift = waveUpperLegLiftAngle + Mathf.Sin(phase) * 10f;
        float lowerSwing = Mathf.Sin(phase) * waveLowerLegSwingAngle;
        float sideSwing = Mathf.Cos(phase) * waveLowerLegSwingAngle * 0.22f;

        ApplyBodyPose(idleBreathAmplitude * 0.5f, 0f, yaw, roll);

        ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, 5f, -8f);
        ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, -5f, 8f);
        ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, -5f, 8f);
        ApplyLegPose(frontLeftUpperLeg, null, upperLift, 0f);

        Transform wavingPart = wavePart != null ? wavePart : frontLeftLowerLeg;
        if (wavingPart != null && initialRotations.TryGetValue(wavingPart, out Quaternion initialRotation))
        {
            Quaternion targetRotation = initialRotation * Quaternion.Euler(lowerSwing, 0f, sideSwing);
            LerpLocalRotation(wavingPart, targetRotation);
        }
    }

    private void AnimateJump()
    {
        float normalizedTime = Mathf.Clamp01(actionTime / Mathf.Max(0.1f, jumpDuration));
        float liftCurve = Mathf.Sin(normalizedTime * Mathf.PI);
        float squash = normalizedTime < 0.22f
            ? -jumpSquashHeight * (1f - normalizedTime / 0.22f)
            : 0f;
        float effectiveJumpHeight = Mathf.Max(jumpHeight, 0.56f);
        float height = liftCurve * effectiveJumpHeight + squash;
        float pitch = Mathf.Sin(normalizedTime * Mathf.PI * 2f) * jumpBodyPitch;

        ApplyBodyPose(height, pitch, 0f, 0f);

        if (normalizedTime < 0.22f)
        {
            float prep = Mathf.SmoothStep(0f, 1f, normalizedTime / 0.22f);
            ApplyLegPose(frontLeftUpperLeg, frontLeftLowerLeg, Mathf.Lerp(16f, -8f, prep), Mathf.Lerp(-24f, -10f, prep));
            ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, Mathf.Lerp(16f, -8f, prep), Mathf.Lerp(-24f, -10f, prep));
            ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, Mathf.Lerp(-18f, 10f, prep), Mathf.Lerp(24f, 8f, prep));
            ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, Mathf.Lerp(-18f, 10f, prep), Mathf.Lerp(24f, 8f, prep));
        }
        else if (normalizedTime < 0.74f)
        {
            ApplyLegPose(frontLeftUpperLeg, frontLeftLowerLeg, -jumpLegTuckAngle, -jumpLegTuckAngle * 0.7f);
            ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, -jumpLegTuckAngle, -jumpLegTuckAngle * 0.7f);
            ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, jumpLegTuckAngle * 0.65f, jumpLegTuckAngle * 0.55f);
            ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, jumpLegTuckAngle * 0.65f, jumpLegTuckAngle * 0.55f);
        }
        else
        {
            float land = Mathf.SmoothStep(0f, 1f, (normalizedTime - 0.74f) / 0.26f);
            ApplyLegPose(frontLeftUpperLeg, frontLeftLowerLeg, Mathf.Lerp(-10f, standUpperLegAngle, land), Mathf.Lerp(-16f, standLowerLegAngle, land));
            ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, Mathf.Lerp(-10f, standUpperLegAngle, land), Mathf.Lerp(-16f, standLowerLegAngle, land));
            ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, Mathf.Lerp(10f, standUpperLegAngle, land), Mathf.Lerp(14f, standLowerLegAngle, land));
            ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, Mathf.Lerp(10f, standUpperLegAngle, land), Mathf.Lerp(14f, standLowerLegAngle, land));
        }

        RestoreWavePartIfSeparate();

        if (normalizedTime >= 1f)
        {
            requestedAction = ActionIdle;
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

    private void ApplyNeutralLegPose()
    {
        ApplyLegPose(frontLeftUpperLeg, frontLeftLowerLeg, 0f, 0f);
        ApplyLegPose(frontRightUpperLeg, frontRightLowerLeg, 0f, 0f);
        ApplyLegPose(rearLeftUpperLeg, rearLeftLowerLeg, 0f, 0f);
        ApplyLegPose(rearRightUpperLeg, rearRightLowerLeg, 0f, 0f);
        RestoreWavePartIfSeparate();
    }

    private void ApplyDiagonalStep(
        Transform frontUpper,
        Transform frontLower,
        Transform rearUpper,
        Transform rearLower,
        float phase,
        float direction
    )
    {
        float swing = Mathf.Sin(phase);
        float lift = Mathf.Max(0f, swing);
        float support = Mathf.Max(0f, -swing);
        float groundedPush = support * legSwingAmplitude * 0.35f * direction;
        float airSwing = lift * legSwingAmplitude * direction;
        float frontUpperAngle = airSwing - groundedPush;
        float rearUpperAngle = airSwing * 0.75f + groundedPush;
        float lowerBend = -(lift * lowerLegBendAmplitude + lift * stepLiftAmplitude);
        float supportLower = support * lowerLegBendAmplitude * 0.15f;

        ApplyLegPose(frontUpper, frontLower, frontUpperAngle, lowerBend + supportLower);
        ApplyLegPose(rearUpper, rearLower, rearUpperAngle, lowerBend * 0.85f + supportLower);
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

    private void RestoreWavePartIfSeparate()
    {
        if (
            wavePart != null
            && wavePart != frontLeftLowerLeg
            && wavePart != frontRightLowerLeg
            && wavePart != rearLeftLowerLeg
            && wavePart != rearRightLowerLeg
        )
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
        float speed = Mathf.Max(legLerpSpeed, poseBlendSpeed);
        target.localRotation = Quaternion.Slerp(
            target.localRotation,
            targetRotation,
            speed * Time.deltaTime
        );
    }

    private float GetTargetMoveVelocity()
    {
        if (currentAction == ActionForward)
        {
            return Mathf.Min(moveSpeed, 0.42f);
        }

        if (currentAction == ActionBackward)
        {
            return -Mathf.Min(moveSpeed, 0.42f);
        }

        return 0f;
    }

    private float GetTargetTurnVelocity()
    {
        if (currentAction == ActionForward || currentAction == ActionBackward)
        {
            return targetTurnDirection * turnSpeed;
        }

        return 0f;
    }

    private bool IsKnownAction(string action)
    {
        return action == ActionIdle
            || action == ActionForward
            || action == ActionBackward
            || action == ActionSit
            || action == ActionWave
            || action == ActionJump
            || action == ActionStand;
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
