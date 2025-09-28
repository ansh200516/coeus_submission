// User-facing boilerplates with solution function
export const USER_BOILERPLATES = {
  // Two Sum - Problem ID: 1
  "sum": {
    python: `def solution(nums, target):
    """
    :type nums: List[int]
    :type target: int
    :rtype: List[int]
    """
    # Write your solution here
    pass`,
    
    javascript: `/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number[]}
 */
function solution(nums, target) {
    // Write your solution here
    
}`,
    
    typescript: `/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number[]}
 */
function solution(nums: number[], target: number): number[] {
    // Write your solution here
    return [];
}`,
    
    java: `/**
 * @param nums An array of integers
 * @param target The target sum
 * @return Indices of the two numbers that add up to target
 */
public int[] solution(int[] nums, int target) {
    // Write your solution here
    return new int[]{};
}`,
    
    csharp: `/**
 * @param nums An array of integers
 * @param target The target sum
 * @return Indices of the two numbers that add up to target
 */
public int[] Solution(int[] nums, int target) {
    // Write your solution here
    return new int[]{};
}`,
    
    php: `/**
 * @param int[] $nums
 * @param int $target
 * @return int[]
 */
function solution($nums, $target) {
    // Write your solution here
    return [];
}`
  },
  
  // Palindrome - Problem ID: 4, 5, 6
  "palindrome": {
    python: `def solution(x):
    """
    :type x: int or str (depending on the problem)
    :rtype: bool or str (depending on the problem)
    """
    # Write your solution here
    pass`,
    
    javascript: `/**
 * @param {number|string} x - Input value (number or string depending on problem)
 * @return {boolean|string} - Result (boolean or string depending on problem)
 */
function solution(x) {
    // Write your solution here
    
}`,
    
    typescript: `/**
 * @param {number|string} x - Input value (number or string depending on problem)
 * @return {boolean|string} - Result (boolean or string depending on problem)
 */
function solution(x: any): any {
    // Write your solution here
    return false; // or "" depending on problem
}`,
    
    java: `/**
 * @param x Input value (could be int or String depending on problem)
 * @return Result (could be boolean or String depending on problem)
 */
public Object solution(Object x) {
    // Write your solution here
    // Return type will depend on the specific problem
    return false; // or "" depending on problem
}`,
    
    csharp: `/**
 * @param x Input value (could be int or string depending on problem)
 * @return Result (could be boolean or string depending on problem)
 */
public object Solution(object x) {
    // Write your solution here
    // Return type will depend on the specific problem
    return false; // or "" depending on problem
}`,
    
    php: `/**
 * @param mixed $x Input value (could be int or string depending on problem)
 * @return mixed Result (could be boolean or string depending on problem)
 */
function solution($x) {
    // Write your solution here
    return false; // or "" depending on problem
}`
  },
  
  // Reverse - Problem ID: 7, 8, 9
  "reverse": {
    python: `def solution(x):
    """
    :type x: int or List[str] or str (depending on the problem)
    :rtype: int or None or str (depending on the problem)
    """
    # Write your solution here
    pass`,
    
    javascript: `/**
 * @param {number|string|string[]} x - Input value (depends on problem)
 * @return {number|string|undefined} - Result (depends on problem)
 */
function solution(x) {
    // Write your solution here
    
}`,
    
    typescript: `/**
 * @param {number|string|string[]} x - Input value (depends on problem)
 * @return {number|string|undefined} - Result (depends on problem)
 */
function solution(x: any): any {
    // Write your solution here
    return 0; // or "" or undefined depending on problem
}`,
    
    java: `/**
 * @param x Input value (could be int, String, or char[] depending on problem)
 * @return Result (could be int, String, or void depending on problem)
 */
public Object solution(Object x) {
    // Write your solution here
    // Return type will depend on the specific problem
    return 0; // or "" depending on problem
}`,
    
    csharp: `/**
 * @param x Input value (could be int, string, or char[] depending on problem)
 * @return Result (could be int, string, or void depending on problem)
 */
public object Solution(object x) {
    // Write your solution here
    // Return type will depend on the specific problem
    return 0; // or "" depending on problem
}`,
    
    php: `/**
 * @param mixed $x Input value (could be int, string, or array depending on problem)
 * @return mixed Result (could be int, string, or void depending on problem)
 */
function solution($x) {
    // Write your solution here
    return 0; // or "" depending on problem
}`
  }
};

// Hidden test boilerplates that will be combined with user code for testing
export const TEST_BOILERPLATES = {
  // Two Sum - Problem ID: 1, 2, 3
  "sum": {
    python: `
# Test code - DO NOT SHOW TO USER
import sys
import json

if __name__ == "__main__":
    lines = sys.stdin.read().strip().split('\\n')
    nums = json.loads(lines[0])
    target = int(lines[1])
    result = solution(nums, target)
    print(json.dumps(result))`,
    
    javascript: `
// Test code - DO NOT SHOW TO USER
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let input = [];
rl.on('line', (line) => {
    input.push(line.trim());
});

rl.on('close', () => {
    const nums = JSON.parse(input[0]);
    const target = parseInt(input[1]);
    const result = solution(nums, target);
    console.log(JSON.stringify(result));
});`,
    
    typescript: `
// Test code - DO NOT SHOW TO USER
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let input: string[] = [];
rl.on('line', (line: string) => {
    input.push(line.trim());
});

rl.on('close', () => {
    const nums: number[] = JSON.parse(input[0]);
    const target: number = parseInt(input[1]);
    const result: number[] = solution(nums, target);
    console.log(JSON.stringify(result));
});`,
    
    java: `
// Test code - DO NOT SHOW TO USER
import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] numsStr = br.readLine().replace("[", "").replace("]", "").split(",");
        int[] nums = new int[numsStr.length];
        for (int i = 0; i < numsStr.length; i++) {
            nums[i] = Integer.parseInt(numsStr[i].trim());
        }
        int target = Integer.parseInt(br.readLine().trim());

        Solution sol = new Solution();
        int[] result = sol.solution(nums, target);
        System.out.println(Arrays.toString(result));
    }
}

class Solution {
    // User code will be inserted here
}`,
    
    csharp: `
// Test code - DO NOT SHOW TO USER
using System;
using System.Linq;

public class Program {
    public static void Main(string[] args) {
        string numsLine = Console.ReadLine();
        string targetLine = Console.ReadLine();

        int[] nums = numsLine.Trim('[', ']').Split(',').Select(x => int.Parse(x.Trim())).ToArray();
        int target = int.Parse(targetLine);

        Solution sol = new Solution();
        int[] result = sol.Solution(nums, target);
        Console.WriteLine($"[{string.Join(", ", result)}]");
    }
}

public class Solution {
    // User code will be inserted here
}`,
    
    php: `<?php
// Test code - DO NOT SHOW TO USER
$input = file_get_contents('php://stdin');
$lines = explode("\\n", trim($input));
$nums = json_decode($lines[0]);
$target = intval($lines[1]);
$result = solution($nums, $target);
echo json_encode($result);
?>`
  },
  
  // Palindrome - Problem ID: 4, 5, 6
  "palindrome": {
    python: `
# Test code - DO NOT SHOW TO USER
import sys

if __name__ == "__main__":
    x = sys.stdin.read().strip()
    # Try to convert to int if it's a numeric palindrome problem
    try:
        x = int(x)
    except:
        # It's a string palindrome problem
        pass
    result = solution(x)
    if isinstance(result, bool):
        print(str(result).lower())
    else:
        print(result)`,
    
    javascript: `
// Test code - DO NOT SHOW TO USER
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (line) => {
    let x = line.trim();
    // Try to convert to number if it's a numeric palindrome problem
    if (!isNaN(x) && !x.includes('"')) {
        x = parseInt(x);
    } else {
        // Remove quotes if it's a string
        x = x.replace(/^"|"$/g, '');
    }
    const result = solution(x);
    if (typeof result === 'boolean') {
        console.log(result.toString());
    } else {
        console.log(result);
    }
    rl.close();
});`,
    
    typescript: `
// Test code - DO NOT SHOW TO USER
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (line: string) => {
    let x: any = line.trim();
    // Try to convert to number if it's a numeric palindrome problem
    if (!isNaN(Number(x)) && !x.includes('"')) {
        x = parseInt(x);
    } else {
        // Remove quotes if it's a string
        x = x.replace(/^"|"$/g, '');
    }
    const result: any = solution(x);
    if (typeof result === 'boolean') {
        console.log(result.toString());
    } else {
        console.log(result);
    }
    rl.close();
});`,
    
    java: `
// Test code - DO NOT SHOW TO USER
import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String input = br.readLine().trim();
        
        Solution sol = new Solution();
        Object result;
        
        // Try to convert to int if it's a numeric palindrome problem
        try {
            int x = Integer.parseInt(input);
            result = sol.solution(x);
        } catch (NumberFormatException e) {
            // It's a string palindrome problem
            // Remove quotes if present
            if (input.startsWith("\"") && input.endsWith("\"")) {
                input = input.substring(1, input.length() - 1);
            }
            result = sol.solution(input);
        }
        
        System.out.println(result);
    }
}

class Solution {
    // User code will be inserted here
}`,
    
    csharp: `
// Test code - DO NOT SHOW TO USER
using System;

public class Program {
    public static void Main(string[] args) {
        string input = Console.ReadLine().Trim();
        
        Solution sol = new Solution();
        object result;
        
        // Try to convert to int if it's a numeric palindrome problem
        if (int.TryParse(input, out int x)) {
            result = sol.Solution(x);
        } else {
            // It's a string palindrome problem
            // Remove quotes if present
            if (input.StartsWith("\"") && input.EndsWith("\"")) {
                input = input.Substring(1, input.Length - 2);
            }
            result = sol.Solution(input);
        }
        
        if (result is bool boolResult) {
            Console.WriteLine(boolResult.ToString().ToLower());
        } else {
            Console.WriteLine(result);
        }
    }
}

public class Solution {
    // User code will be inserted here
}`,
    
    php: `<?php
// Test code - DO NOT SHOW TO USER
$input = trim(file_get_contents('php://stdin'));

// Try to convert to int if it's a numeric palindrome problem
if (is_numeric($input) && !strpos($input, '"')) {
    $x = intval($input);
} else {
    // It's a string palindrome problem
    // Remove quotes if present
    $x = trim($input, '"');
}

$result = solution($x);
if (is_bool($result)) {
    echo $result ? 'true' : 'false';
} else {
    echo $result;
}
?>`
  },
  
  // Reverse - Problem ID: 7, 8, 9
  "reverse": {
    python: `
# Test code - DO NOT SHOW TO USER
import sys
import json

if __name__ == "__main__":
    input_str = sys.stdin.read().strip()
    
    # Check if input is an array of characters (for reverse string problem)
    if input_str.startswith('[') and input_str.endswith(']'):
        x = json.loads(input_str)
    else:
        # Try to convert to int for reverse integer problem
        try:
            x = int(input_str)
        except:
            # It's a string reverse problem
            x = input_str.strip('"')
    
    result = solution(x)
    
    # Handle different return types
    if isinstance(result, list):
        print(json.dumps(result))
    else:
        print(result)`,
    
    javascript: `
// Test code - DO NOT SHOW TO USER
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (line) => {
    let x;
    
    // Check if input is an array of characters (for reverse string problem)
    if (line.trim().startsWith('[') && line.trim().endsWith(']')) {
        x = JSON.parse(line);
    } else {
        // Try to convert to number for reverse integer problem
        if (!isNaN(line) && !line.includes('"')) {
            x = parseInt(line);
        } else {
            // It's a string reverse problem
            x = line.replace(/^"|"$/g, '');
        }
    }
    
    const result = solution(x);
    
    // Handle different return types
    if (Array.isArray(result)) {
        console.log(JSON.stringify(result));
    } else {
        console.log(result);
    }
    
    rl.close();
});`,
    
    typescript: `
// Test code - DO NOT SHOW TO USER
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (line: string) => {
    let x: any;
    
    // Check if input is an array of characters (for reverse string problem)
    if (line.trim().startsWith('[') && line.trim().endsWith(']')) {
        x = JSON.parse(line);
    } else {
        // Try to convert to number for reverse integer problem
        if (!isNaN(Number(line)) && !line.includes('"')) {
            x = parseInt(line);
        } else {
            // It's a string reverse problem
            x = line.replace(/^"|"$/g, '');
        }
    }
    
    const result: any = solution(x);
    
    // Handle different return types
    if (Array.isArray(result)) {
        console.log(JSON.stringify(result));
    } else {
        console.log(result);
    }
    
    rl.close();
});`,
    
    java: `
// Test code - DO NOT SHOW TO USER
import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String input = br.readLine().trim();
        
        Solution sol = new Solution();
        Object result;
        
        // Check if input is an array of characters (for reverse string problem)
        if (input.startsWith("[") && input.endsWith("]")) {
            String[] charArray = input.substring(1, input.length() - 1).split(",");
            char[] chars = new char[charArray.length];
            for (int i = 0; i < charArray.length; i++) {
                chars[i] = charArray[i].trim().replace("\"", "").charAt(0);
            }
            result = sol.solution(chars);
        } else {
            // Try to convert to int for reverse integer problem
            try {
                int x = Integer.parseInt(input);
                result = sol.solution(x);
            } catch (NumberFormatException e) {
                // It's a string reverse problem
                if (input.startsWith("\"") && input.endsWith("\"")) {
                    input = input.substring(1, input.length() - 1);
                }
                result = sol.solution(input);
            }
        }
        
        // Handle different return types
        if (result instanceof char[]) {
            System.out.print("[");
            char[] chars = (char[]) result;
            for (int i = 0; i < chars.length; i++) {
                System.out.print("\"" + chars[i] + "\"");
                if (i < chars.length - 1) System.out.print(",");
            }
            System.out.println("]");
        } else {
            System.out.println(result);
        }
    }
}

class Solution {
    // User code will be inserted here
}`,
    
    csharp: `
// Test code - DO NOT SHOW TO USER
using System;
using System.Linq;

public class Program {
    public static void Main(string[] args) {
        string input = Console.ReadLine().Trim();
        
        Solution sol = new Solution();
        object result;
        
        // Check if input is an array of characters (for reverse string problem)
        if (input.StartsWith("[") && input.EndsWith("]")) {
            string[] charArray = input.Substring(1, input.Length - 2).Split(',');
            char[] chars = new char[charArray.Length];
            for (int i = 0; i < charArray.Length; i++) {
                chars[i] = charArray[i].Trim().Replace("\"", "")[0];
            }
            result = sol.Solution(chars);
        } else {
            // Try to convert to int for reverse integer problem
            if (int.TryParse(input, out int x)) {
                result = sol.Solution(x);
            } else {
                // It's a string reverse problem
                if (input.StartsWith("\"") && input.EndsWith("\"")) {
                    input = input.Substring(1, input.Length - 2);
                }
                result = sol.Solution(input);
            }
        }
        
        // Handle different return types
        if (result is char[] chars) {
            Console.Write("[");
            for (int i = 0; i < chars.Length; i++) {
                Console.Write($"\"{chars[i]}\"");
                if (i < chars.Length - 1) Console.Write(",");
            }
            Console.WriteLine("]");
        } else {
            Console.WriteLine(result);
        }
    }
}

public class Solution {
    // User code will be inserted here
}`,
    
    php: `<?php
// Test code - DO NOT SHOW TO USER
$input = trim(file_get_contents('php://stdin'));

// Check if input is an array of characters (for reverse string problem)
if (strpos($input, '[') === 0 && strrpos($input, ']') === strlen($input) - 1) {
    $x = json_decode($input);
} else {
    // Try to convert to int for reverse integer problem
    if (is_numeric($input) && !strpos($input, '"')) {
        $x = intval($input);
    } else {
        // It's a string reverse problem
        $x = trim($input, '"');
    }
}

$result = solution($x);

// Handle different return types
if (is_array($result)) {
    echo json_encode($result);
} else {
    echo $result;
}
?>`
  }
};
