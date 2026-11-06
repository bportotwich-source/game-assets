// Coloque na câmera do jogador. Aperte E olhando para uma porta a até 2 m.
using UnityEngine;

public class DoorInteractor : MonoBehaviour
{
    public float reach = 2f;
    public KeyCode key = KeyCode.E;

    void Update()
    {
        if (!Input.GetKeyDown(key)) return;
        if (Physics.Raycast(transform.position, transform.forward, out RaycastHit hit, reach))
        {
            var door = hit.collider.GetComponentInParent<KitDoor>();
            if (door) door.Interact();
        }
    }
}
