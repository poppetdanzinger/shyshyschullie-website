using UnityEngine;
using System.Collections;

public class ClickController : MonoBehaviour
{
	//this is how far away from the player an object can still be clicked.
	float range;
	
	void Start ()
	{
		range = 10;
	}
	
	// Update is called once per frame
	void Update ()
	{
		if (Input.GetMouseButtonDown (0)) {
			Vector3 pos = Camera.main.transform.position;
			RaycastHit rayCastHit = new RaycastHit ();
			//draw a line in 3D space, starting at our camera, and pointing in the direction we are looking.
			//if that line collides with a gameobject, store the collision information into rayCastHit.
			if (Physics.Linecast (pos, pos + Camera.main.transform.forward * range, out rayCastHit, 1)) {
				//get the gameobject we hit, the hitObject, stored in the rayCastHit we just found
				GameObject hitObject = rayCastHit.transform.gameObject;
				
				ClickTransmitter ct = hitObject.GetComponent<ClickTransmitter> ();
				//if the gameobject we clicked has an attached ClickTransmitter, then do this:
				if (ct != null) {
					//send the transmit code from the ClickTransmitter to all ClickAntenna in the game.
					foreach (ClickAntenna ca in FindObjectsOfType<ClickAntenna>())
						ca.receiveTransmitCode (ct.transmitCode);
				}
				
			}
		}
	}
}
