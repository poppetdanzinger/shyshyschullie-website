using UnityEngine;
using System.Collections;

[System.Serializable]
public class ClickAntenna : MonoBehaviour
{
	//when a ClickTransmitter is clicked, every ClickAntenna with the same transmitCode will react.
	public string transmitCode = "something";
	//this is how much the clickAntenna gameobject will move if it is send the right transmit code.
	public Vector3 newPositionOffset = new Vector3 (0, 5, 0);
	//this is how long the move will take in seconds.
	public float moveDuration = 2;
	
	//this keeps track of where the gameobject started in the first place.
	private Vector3 startPosition;
	//this keeps track of how many seconds have passed since the antenna was activated.
	private float moveTimer;
	//this is whether the gameobject is in a moving state or not.
	private bool isMoving;
	
	void Start ()
	{
		//initialize our variables
		moveTimer = 0;
		isMoving = false;
		startPosition = new Vector3 (transform.position.x, transform.position.y, transform.position.z);
	}
	
	void Update ()
	{
		if (isMoving) {
			moveTimer += Time.deltaTime;
			//the ratio is what percent of our move distance we have covered so far.
			float ratio = moveTimer / moveDuration;
			//set our position to our start position, plus the offset times our ratio percent
			transform.position = new Vector3 (startPosition.x + ratio * newPositionOffset.x,
			                                  startPosition.y + ratio * newPositionOffset.y,
			                                  startPosition.z + ratio * newPositionOffset.z);
			if (moveTimer > moveDuration) {
				//this is when we are done moving.
				isMoving = false;
				transform.position = new Vector3 (startPosition.x + newPositionOffset.x,
				                                  startPosition.y + newPositionOffset.y,
				                                  startPosition.z + newPositionOffset.z);
			}
		}
	}
	
	public void receiveTransmitCode (string code)
	{
		//this is a good place to add special cases for different codes, like:
		//if(code=="gold coin")
		//then add one to gold counter, etc.
		
		if (code==transmitCode)
			isMoving = true;
		
	}
}
