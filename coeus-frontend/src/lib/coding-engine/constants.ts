export const LANGUAGE_VERSIONS = {
  python: "3.10.0",
  javascript: "18.15.0",
  typescript: "5.0.3",
  java: "15.0.2",
  csharp: "6.12.0",
  php: "8.2.3",
};

export const CODE_SNIPPETS = {
  python: `\ndef greet(name):\n\tprint("Hello, " + name + "!")\n\ngreet("Alex")\n`,
  javascript: `\nfunction greet(name) {\n\tconsole.log("Hello, " + name + "!");\n}\n\ngreet("Alex");\n`,
  typescript: `\ntype Params = {\n\tname: string;\n}\n\nfunction greet(data: Params) {\n\tconsole.log("Hello, " + data.name + "!");\n}\n\ngreet({ name: "Alex" });\n`,
  java: `\npublic class HelloWorld {\n\tpublic static void main(String[] args) {\n\t\tSystem.out.println("Hello World");\n\t}\n}\n`,
  csharp:
    'using System;\n\nnamespace HelloWorld\n{\n\tclass Hello { \n\t\tstatic void Main(string[] args) {\n\t\t\tConsole.WriteLine("Hello World in C#");\n\t\t}\n\t}\n}\n',
  php: "<?php\n\n$name = 'Alex';\necho $name;\n",
};

export const PROBLEM_BOILERPLATES = {
  // Two Sum problem boilerplates
  1: {
    python: `# Two Sum
# Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

def twoSum(nums, target):
    # Write your solution here
    pass

# Test code - DO NOT MODIFY
import sys
import json

if __name__ == "__main__":
    lines = sys.stdin.read().strip().split('\\n')
    nums = json.loads(lines[0])
    target = int(lines[1])
    result = twoSum(nums, target)
    print(json.dumps(result))`,

    javascript: `// Two Sum
// Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

function twoSum(nums, target) {
    // Write your solution here

}

// Test code - DO NOT MODIFY
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
    const result = twoSum(nums, target);
    console.log(JSON.stringify(result));
});`,

    java: `import java.util.*;
import java.io.*;

public class Solution {
    // Two Sum
    // Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

    public int[] twoSum(int[] nums, int target) {
        // Write your solution here
        return new int[]{};
    }

    // Test code - DO NOT MODIFY
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String[] numsStr = br.readLine().replace("[", "").replace("]", "").split(",");
        int[] nums = new int[numsStr.length];
        for (int i = 0; i < numsStr.length; i++) {
            nums[i] = Integer.parseInt(numsStr[i].trim());
        }
        int target = Integer.parseInt(br.readLine().trim());

        Solution sol = new Solution();
        int[] result = sol.twoSum(nums, target);
        System.out.println(Arrays.toString(result));
    }
}`,

    csharp: `using System;
using System.Linq;

public class Solution {
    // Two Sum
    // Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

    public int[] TwoSum(int[] nums, int target) {
        // Write your solution here
        return new int[]{};
    }

    // Test code - DO NOT MODIFY
    public static void Main(string[] args) {
        string numsLine = Console.ReadLine();
        string targetLine = Console.ReadLine();

        int[] nums = numsLine.Trim('[', ']').Split(',').Select(x => int.Parse(x.Trim())).ToArray();
        int target = int.Parse(targetLine);

        Solution sol = new Solution();
        int[] result = sol.TwoSum(nums, target);
        Console.WriteLine($"[{string.Join(", ", result)}]");
    }
}`,

    php: `<?php
// Two Sum
// Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

function twoSum($nums, $target) {
    // Write your solution here
    return [];
}

// Test code - DO NOT MODIFY
$input = file_get_contents('php://stdin');
$lines = explode("\\n", trim($input));
$nums = json_decode($lines[0]);
$target = intval($lines[1]);
$result = twoSum($nums, $target);
echo json_encode($result);
?>`
  },

  // Palindrome Number problem boilerplates
  2: {
    python: `# Palindrome Number
# Given an integer x, return true if x is a palindrome, and false otherwise.

def isPalindrome(x):
    # Write your solution here
    pass

# Test code - DO NOT MODIFY
import sys

if __name__ == "__main__":
    x = int(sys.stdin.read().strip())
    result = isPalindrome(x)
    print(str(result).lower())`,

    javascript: `// Palindrome Number
// Given an integer x, return true if x is a palindrome, and false otherwise.

function isPalindrome(x) {
    // Write your solution here

}

// Test code - DO NOT MODIFY
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (line) => {
    const x = parseInt(line.trim());
    const result = isPalindrome(x);
    console.log(result.toString());
    rl.close();
});`,

    java: `import java.util.*;
import java.io.*;

public class Solution {
    // Palindrome Number
    // Given an integer x, return true if x is a palindrome, and false otherwise.

    public boolean isPalindrome(int x) {
        // Write your solution here
        return false;
    }

    // Test code - DO NOT MODIFY
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int x = Integer.parseInt(br.readLine().trim());

        Solution sol = new Solution();
        boolean result = sol.isPalindrome(x);
        System.out.println(result);
    }
}`,

    csharp: `using System;

public class Solution {
    // Palindrome Number
    // Given an integer x, return true if x is a palindrome, and false otherwise.

    public bool IsPalindrome(int x) {
        // Write your solution here
        return false;
    }

    // Test code - DO NOT MODIFY
    public static void Main(string[] args) {
        int x = int.Parse(Console.ReadLine().Trim());

        Solution sol = new Solution();
        bool result = sol.IsPalindrome(x);
        Console.WriteLine(result.ToString().ToLower());
    }
}`,

    php: `<?php
// Palindrome Number
// Given an integer x, return true if x is a palindrome, and false otherwise.

function isPalindrome($x) {
    // Write your solution here
    return false;
}

// Test code - DO NOT MODIFY
$x = intval(trim(file_get_contents('php://stdin')));
$result = isPalindrome($x);
echo $result ? 'true' : 'false';
?>`
  },

  // Reverse Integer problem boilerplates
  3: {
    python: `# Reverse Integer
# Given a signed 32-bit integer x, return x with its digits reversed.

def reverse(x):
    # Write your solution here
    pass

# Test code - DO NOT MODIFY
import sys

if __name__ == "__main__":
    x = int(sys.stdin.read().strip())
    result = reverse(x)
    print(result)`,

    javascript: `// Reverse Integer
// Given a signed 32-bit integer x, return x with its digits reversed.

function reverse(x) {
    // Write your solution here

}

// Test code - DO NOT MODIFY
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (line) => {
    const x = parseInt(line.trim());
    const result = reverse(x);
    console.log(result);
    rl.close();
});`,

    java: `import java.util.*;
import java.io.*;

public class Solution {
    // Reverse Integer
    // Given a signed 32-bit integer x, return x with its digits reversed.

    public int reverse(int x) {
        // Write your solution here
        return 0;
    }

    // Test code - DO NOT MODIFY
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int x = Integer.parseInt(br.readLine().trim());

        Solution sol = new Solution();
        int result = sol.reverse(x);
        System.out.println(result);
    }
}`,

    csharp: `using System;

public class Solution {
    // Reverse Integer
    // Given a signed 32-bit integer x, return x with its digits reversed.

    public int Reverse(int x) {
        // Write your solution here
        return 0;
    }

    // Test code - DO NOT MODIFY
    public static void Main(string[] args) {
        int x = int.Parse(Console.ReadLine().Trim());

        Solution sol = new Solution();
        int result = sol.Reverse(x);
        Console.WriteLine(result);
    }
}`,

    php: `<?php
// Reverse Integer
// Given a signed 32-bit integer x, return x with its digits reversed.

function reverse($x) {
    // Write your solution here
    return 0;
}

// Test code - DO NOT MODIFY
$x = intval(trim(file_get_contents('php://stdin')));
$result = reverse($x);
echo $result;
?>`
  }
};
