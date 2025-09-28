import {
  Box,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Button,
  Text,
  Badge,
  HStack,
} from "@chakra-ui/react";

const QuestionSelector = ({ questions, selectedQuestion, onSelect, disabled = false }) => {
  const getDifficultyColor = (difficulty) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'green';
      case 'medium':
        return 'yellow';
      case 'hard':
        return 'red';
      default:
        return 'gray';
    }
  };

  if (disabled && selectedQuestion) {
    return (
      <Box mb={4}>
        <Text mb={2} fontSize="lg" color="white" fontWeight="bold">
          Interview Problem:
        </Text>
        <Box
          bg="gray.700"
          color="white"
          p={3}
          borderRadius="md"
          w="100%"
          border="1px solid"
          borderColor="gray.600"
        >
          <HStack justify="space-between">
            <Text fontWeight="medium">
              {selectedQuestion.id}. {selectedQuestion.title}
            </Text>
            <Badge 
              colorScheme={getDifficultyColor(selectedQuestion.difficulty)} 
              variant="solid"
              size="sm"
            >
              {selectedQuestion.difficulty}
            </Badge>
          </HStack>
        </Box>
      </Box>
    );
  }

  return (
    <Box mb={4}>
      <Text mb={2} fontSize="lg" color="white" fontWeight="bold">
        Select Problem:
      </Text>
      <Menu>
        <MenuButton
          as={Button}
          bg="gray.700"
          color="white"
          _hover={{ bg: "gray.600" }}
          _active={{ bg: "gray.600" }}
          w="100%"
          textAlign="left"
        >
          {selectedQuestion 
            ? `${selectedQuestion.id}. ${selectedQuestion.title}`
            : "Choose a problem..."
          }
        </MenuButton>
        <MenuList bg="gray.800" borderColor="gray.600">
          {questions.map((question) => (
            <MenuItem
              key={question.id}
              bg="transparent"
              color="white"
              _hover={{ bg: "gray.700" }}
              _focus={{ bg: "gray.700" }}
              onClick={() => onSelect(question)}
            >
              <HStack justify="space-between" w="100%">
                <Text>
                  {question.id}. {question.title}
                </Text>
                <Badge 
                  colorScheme={getDifficultyColor(question.difficulty)} 
                  variant="solid"
                  size="sm"
                >
                  {question.difficulty}
                </Badge>
              </HStack>
            </MenuItem>
          ))}
        </MenuList>
      </Menu>
    </Box>
  );
};

export default QuestionSelector;
