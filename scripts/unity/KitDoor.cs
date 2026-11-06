// Porta do kit (Unity). Coloque no GameObject da folha (door_leaf_*.glb, importado com glTFast).
// O pivô já está na dobradiça. Adicione um BoxCollider na folha para o jogador esbarrar e para o raio achar a porta.
using System.Collections;
using UnityEngine;

public class KitDoor : MonoBehaviour
{
    [Tooltip("Valor 'open - closed' do building_layout.json")]
    public float openAngle = 70f;
    public float duration = 0.35f;
    public bool startOpen = false;
    public bool locked = false;

    public bool IsOpen { get; private set; }
    Quaternion closedRot;
    Coroutine anim;

    void Awake()
    {
        closedRot = transform.localRotation;
        if (startOpen) { IsOpen = true; transform.localRotation = closedRot * Quaternion.Euler(0, -openAngle, 0); }
    }

    public void Interact()
    {
        if (locked) return;
        SetOpen(!IsOpen);
    }

    public void SetOpen(bool open)
    {
        IsOpen = open;
        if (anim != null) StopCoroutine(anim);
        anim = StartCoroutine(Rotate(open ? closedRot * Quaternion.Euler(0, -openAngle, 0) : closedRot));
    }

    IEnumerator Rotate(Quaternion target)
    {
        Quaternion from = transform.localRotation; float t = 0;
        while (t < 1) { t += Time.deltaTime / duration; transform.localRotation = Quaternion.Slerp(from, target, Mathf.SmoothStep(0, 1, t)); yield return null; }
        transform.localRotation = target;
    }
}
