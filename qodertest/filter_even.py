def filter_even_descending(numbers):
    """
    Takes a list of integers and returns a new list containing only the even numbers,
    sorted in descending order.
    
    Args:
        numbers: A list of integers
        
    Returns:
        A list of even integers sorted in descending order
    """
    # Filter even numbers using list comprehension
    even_numbers = [num for num in numbers if num % 2 == 0]
    
    # Sort in descending order
    return sorted(even_numbers, reverse=True)


def group_anagrams(words):
    """
    Takes a list of strings and groups them into lists of anagrams.
    
    Args:
        words: A list of strings
        
    Returns:
        A list of lists, where each inner list contains anagrams
    """
    from collections import defaultdict
    
    # Dictionary to group anagrams by their sorted characters
    anagram_map = defaultdict(list)
    
    for word in words:
        # Sort the characters in each word to create a key
        # Words that are anagrams will have the same sorted key
        key = ''.join(sorted(word.lower()))
        anagram_map[key].append(word)
    
    # Return the grouped anagrams as a list of lists
    return list(anagram_map.values())


# Test examples
if __name__ == "__main__":
    # Test filter_even_descending
    test_list = [3, 8, 1, 6, 2, 9, 4, 5, 10]
    result = filter_even_descending(test_list)
    print(f"Input: {test_list}")
    print(f"Output: {result}")
    
    # Additional test cases
    print(f"\nTest with negative numbers: {filter_even_descending([-5, -2, 3, 4, -8])}")
    print(f"Test with empty list: {filter_even_descending([])}")
    print(f"Test with all odd numbers: {filter_even_descending([1, 3, 5, 7])}")
    
    # Test group_anagrams
    print("\n" + "="*50)
    print("Testing group_anagrams:")
    print("="*50)
    
    test_words = ["listen", "silent", "hello", "world", "enlist", "dormitory", "dirty room"]
    result_anagrams = group_anagrams(test_words)
    print(f"Input: {test_words}")
    print(f"Output: {result_anagrams}")
    
    # Additional test cases for anagrams
    print(f"\nTest with single words: {group_anagrams(['cat', 'dog', 'rat'])}")
    print(f"Test with duplicates: {group_anagrams(['bat', 'tab', 'bat', 'cat'])}")
    print(f"Test with case sensitivity: {group_anagrams(['Listen', 'Silent', 'enlist'])}")