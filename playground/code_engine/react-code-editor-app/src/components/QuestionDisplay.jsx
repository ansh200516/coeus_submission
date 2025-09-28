import {
  Box,
  Text,
  Heading,
  Badge,
  VStack,
  HStack,
  Divider,
  UnorderedList,
  ListItem,
  Code,
} from "@chakra-ui/react";

const QuestionDisplay = ({ question }) => {
  if (!question) {
    return (
      <Box p={4} bg="gray.800" borderRadius="md" border="1px solid" borderColor="gray.600">
        <Text color="gray.400">Select a question to get started</Text>
      </Box>
    );
  }

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

  return (
    <Box p={4} bg="gray.800" borderRadius="md" border="1px solid" borderColor="gray.600" h="100%" overflowY="auto">
      <VStack align="start" spacing={4}>
        {/* Title and Difficulty */}
        <HStack justify="space-between" w="100%">
          <Heading size="md" color="white">
            {question.id}. {question.title}
          </Heading>
          <Badge colorScheme={getDifficultyColor(question.difficulty)} variant="solid">
            {question.difficulty}
          </Badge>
        </HStack>

        <Divider borderColor="gray.600" />

        {/* Description */}
        <Box>
          <Text color="gray.200" lineHeight="1.6" whiteSpace="pre-line">
            {question.description}
          </Text>
        </Box>

        {/* Examples */}
        {question.examples && question.examples.length > 0 && (
          <Box w="100%">
            <Heading size="sm" color="white" mb={3}>
              Examples:
            </Heading>
            <VStack align="start" spacing={3}>
              {question.examples.map((example, index) => (
                <Box key={index} p={3} bg="gray.700" borderRadius="md" w="100%">
                  <Text color="white" fontWeight="bold">
                    Example {index + 1}:
                  </Text>
                  <Text color="gray.300" mt={1}>
                    <strong>Input:</strong> <Code bg="gray.600" color="gray.200">{example.input}</Code>
                  </Text>
                  <Text color="gray.300" mt={1}>
                    <strong>Output:</strong> <Code bg="gray.600" color="gray.200">{example.output}</Code>
                  </Text>
                  {example.explanation && (
                    <Text color="gray.300" mt={1}>
                      <strong>Explanation:</strong> {example.explanation}
                    </Text>
                  )}
                </Box>
              ))}
            </VStack>
          </Box>
        )}

        {/* Constraints */}
        {question.constraints && question.constraints.length > 0 && (
          <Box w="100%">
            <Heading size="sm" color="white" mb={3}>
              Constraints:
            </Heading>
            <UnorderedList color="gray.300" spacing={1}>
              {question.constraints.map((constraint, index) => (
                <ListItem key={index}>
                  <Code bg="gray.700" color="gray.200" fontSize="sm">{constraint}</Code>
                </ListItem>
              ))}
            </UnorderedList>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default QuestionDisplay;
