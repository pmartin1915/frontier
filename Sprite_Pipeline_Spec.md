FRONTIER: Sprite Generation & FSM Pipeline Spec

Reference: GDD v4.0 — Section 7.4 (Sprite & Animation State Management) 
+1

1. Global Animation Rules
To prevent texture bloat, jitter, and accessory bugs across 7 biomes and 6 time-of-day palettes, all animatable entities strictly adhere to the following rules:
+1


Directional Lock: All base sprites and directional accessories are rendered facing strictly to the right. Leftward movement is handled at runtime via Phaser's flipX transform.
+1


Accessory Layers: Character-specific visual elements (hats, ponchos, saddlery) are rendered as separate transparent-background overlay sprites that track the parent sprite's position and animation frame. Directional accessories (like a rifle holster) are flagged as flip-exempt in the runtime utility.
+1


Frame-Locked Foot Placement: walk and run cycles pin the contact frame to the sprite's Y-position anchor to prevent sliding. The frameRate multiplier syncs to the game's pace state (conservative/normal/hard push).
+1

2. The Universal Animation State Machine (FSM)
Every character and animal utilizes this exact 7-row grid:


Row 0 (idle): 4 frames 


Row 1 (walk): 8 frames 


Row 2 (run): 6 frames 


Row 3 (mount/dismount): 4 frames 


Row 4 (ride): 6 frames 


Row 5 (interact): 4–8 frames depending on context 


Row 6 (injured): 2 frames 

3. Completed Asset Manifest & FSM Mapping

Asset 1: Camp Pet (Grey Mouser Cat) 


Description: Small grey female cat. 

FSM Mapping: Row 1 walk is a low prowl; Row 3 is leaping into wagon; Row 4 is curled up riding; Row 5 is batting/hunting vermin. 


Asset 2: Base Player Character 

Description: Male, fair skin, short light brown hair, square glasses, light blue eyes. Dressed in basic canvas trail clothes.

Accessories: None (Base layer only).


Asset 3: Primary Riding Horse 

Description: Sturdy, unbranded bay horse.

Accessories: Base horse is bare.


Accessory Overlay 3A (Saddle & Tack): Transparent layer containing saddle, stirrups, saddlebags (10-unit water/15-unit food capacity), and an asymmetric rifle holster (flip-exempt).


Asset 4: Elias Coe (Companion - Ex-Soldier) 

Description: Graying beard, faded Union sack coat and trousers. Rigid military posture. 


FSM Mapping: Row 5 (interact) is checking a compass/map (Navigation skill).

Accessory Overlay 4A (Headwear): Weathered Union army kepi hat.


Asset 5: Prairie Schooner Wagon 


Description: Large heavy-duty wooden wagon, white canvas bonnet, side-lashed water barrels (80-unit capacity). Rendered without draft animals attached.

FSM Mapping: Row 1 (walk) rolling slowly; Row 2 (run) violent bouncing; Row 3 (mount) front/rear canvas flaps open; Row 5 (interact) side canvas rolled up exposing cargo; Row 6 (injured) broken wheel / tilted axle.
+1

Asset 6: Heavy Draft Horse

Description: Thicker neck, heavy feathering, broad chest. Distinct from the riding horse.

Accessories: Base horse is bare (unhitched).

Accessory Overlay 6A (Harness): Heavy leather pulling collar, hames, and traces.


Asset 7: Luisa Vega (Companion - Healer) 


Description: Mexican-Apache heritage. Practical trail blouse and split riding skirt, hair tied back.


FSM Mapping: Row 5 (interact) is kneeling and grinding a poultice/inspecting plants (Medicine skill).

Accessory Overlay 7A (Outerwear): Woven, earth-toned Mexican serape.


Asset 8: Tom Blanchard (Companion - Drifter) 


Description: Young, slightly messy hair, nervous energy, plain work shirt and canvas pants. 


FSM Mapping: Row 5 (interact) is crouching, aiming rifle, and skinning game (Hunting skill). Row 6 (injured) is curled tightly ("frozen" under pressure).
+1

Accessory Overlay 8A (Headwear & Neck): Weathered wide-brimmed cowboy hat and tied bandana.

Once Claude has this loaded into his context, he will be perfectly aligned with the visual constraints we've built.