package no.uis.dat240.assignment3;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
public class MarvelGraphController {

	private HashMap<String, HashSet<String>> figMap;
	
	private class MarvTok {
        public final String key, value;
        public MarvTok(String key, String value) {
            this.key = key;
            this.value = value;
        }
    }

	public MarvelGraphController() {
		// Create the Marvel Map from the marvel file.
		figMap = createMap();
	}
	
	private HashMap<String, HashSet<String>> createMap() {
		// Read the file for makeing it into HashMap
        List<String> data = readFile("marvel-hero-network.csv");
        
        // Make a hashMap out of the readed data.
        return hashData(data);
    }
	
	private List<String> readFile(String nameOfFile) {
		// Make an arraylist for the readed lines in the marvelfile. 
		List<String> textList = new ArrayList<String>();
		String lineTextList;
		
		// Try read the textfile, if it is not found raise an error.
		try {
			BufferedReader read = new BufferedReader(new FileReader(nameOfFile));
			
			// While the reader is not null, add line to lines. 
			while ((lineTextList = read.readLine()) != null) {
				textList.add(lineTextList);
			}
			
			// After the whole file is readed, close the reader.
			read.close();
			return textList;
		} catch (IOException e) {
			System.out.println("Something is wrong with the label file");
			return null;
		}
    }
	
	private HashMap<String, HashSet<String>> hashData(List<String> list) {
		// Make the hashmap for fill in. 
        HashMap<String, HashSet<String>> map = new HashMap<>();
        
        // go throw each element in the marvel text file. 
        for (String element : list) {
        	
        	// Split each line in different keys and value pair. 
            List<MarvTok> keyValuePair = keyValuePairMaker(element);
            
            // Go throw each key in the keyValuePair
            for (MarvTok key : keyValuePair) {
            	// check if the map contains any key of same sort, if not put that key to the map.
                if (!map.containsKey(key.key)) {
                    map.put(key.key, new HashSet<String>());
                }
                // and add the value to the respectiv key. 
                map.get(key.key).add(key.value);
            }
        }
        return map;
    }
	
	private List<MarvTok> keyValuePairMaker(String listElement) {
        List<MarvTok> fileMapping = new ArrayList<>();
        
        // split the listElement if it is an "," in the element.
        String[] splitByComma = listElement.toLowerCase().trim().split(",");
        
        // Split it up in left and right for the Comma. 
        String left = splitByComma[0];
        String right = splitByComma[1];
        
        // Split it by the "/". 
		String splitBySlash = "/";
		
		// divide the left and rigth into Heros or other lists. 
        String[] heroes = left.split(splitBySlash);
        String[] other = right.split(splitBySlash);
        
        // go throw each hero in the heros list.
        for (String element : heroes) {
			String otherElement = other.length > 1 ? right : other[0];
            fileMapping.add(new MarvTok(element.trim(), otherElement.trim()));
        }
        
        // go throw each element in the other list.
        for (String element : other) {
			String heroElement = heroes.length > 1 ? left : heroes[0];
            fileMapping.add(new MarvTok(element.trim(), heroElement.trim()));
        }

        return fileMapping;
    }
	
	@RequestMapping("/")
	public String index() {
		return "Greetings from Spring Boot!";
	}
	
	@GetMapping(path = "/degree", produces = "application/json;charset=UTF-8")
	@ResponseBody
	public Map getNodeDegree(@RequestParam String id) {
		// Convert the ID to lowerCase.
		String lowerID = id.toLowerCase();

		// Check whether the key is in the map, if not throw an exception.
		if (!figMap.containsKey(lowerID)) {
			throw new NodeNotFoundException();
		}

		// if it is in the map, make a new map of node as key and neighbors as value.
		HashMap<String, Object> degreeMap = new HashMap<>();
		degreeMap.put("Node", lowerID);
		degreeMap.put("Degree", figMap.get(lowerID).size());
		return degreeMap;
	}
	
	@GetMapping(path = "/neighbors", produces = "application/json;charset=UTF-8")
	@ResponseBody
	public Map getNodeNeighbors(@RequestParam String id) {
		// Convert the ID to lowerCase.
		String lowerID = id.toLowerCase();

		// Check whether the key is in the map, if not throw an exception.
		if (!figMap.containsKey(lowerID)) {
			throw new NodeNotFoundException();
		}

		// if it is in the map, make a new map of node as key and neighbors as value.
		HashMap<String, Object> neighborsMap = new HashMap<>();
		neighborsMap.put("Node", lowerID);
		neighborsMap.put("Neighbors", figMap.get(lowerID));
		return neighborsMap;
	}
	
	@GetMapping(path = "/checkedge", produces = "application/json;charset=UTF-8")
	@ResponseBody
	public Map checkNodeEdge(@RequestParam String id1, @RequestParam String id2) {
		// Convert the IDs to lowerCase.
		String lowerID1 = id1.toLowerCase();
		String lowerID2 = id2.toLowerCase();

		// Check whether on of the keys are in the map, if not throw an exception.
		if (!figMap.containsKey(lowerID1) || !figMap.containsKey(lowerID2)) {
			throw new NodeNotFoundException();
		}

		// if it is in the map, make a new map of node as key and neighbors as value.
		HashMap<String, Object> edgeMap = new HashMap<>();
		edgeMap.put("Node1", lowerID1);
		edgeMap.put("Node2", lowerID2);
		edgeMap.put("EdgeExists", figMap.get(lowerID1).contains(lowerID2));
		return edgeMap;
	}
	
	@ResponseStatus(code = HttpStatus.NOT_FOUND, reason = "Given node id not found!")
	public class NodeNotFoundException extends RuntimeException {
	}

}
