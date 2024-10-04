import axios from "axios";

export const getAIMessage = async (userQuery) => {
  try {
    // Define the API endpoint
    const url = "http://localhost:3000/query"; 

    // Send a POST request to the backend API
    const response = await axios.post(url, {
      question: userQuery 
    });

    // Return the AI message from the backend
    return {
      role: "assistant",
      content: response.data.answer 
    };
  } catch (error) {
    console.error("Error fetching the AI message:", error);
    return {
      role: "assistant",
      content: "There was an error connecting to the AI server. Please try again later."
    };
  }
};
