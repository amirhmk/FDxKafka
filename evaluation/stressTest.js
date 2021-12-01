import fetch from "node-fetch";
import { backOff } from "exponential-backoff";
 
const callClient = async (broker, client_id, channel) => {
    const URLWithParm = `https://us-west1-manifest-design-328217.cloudfunctions.net/kafkaclient?broker=${broker}&channel=${channel}&client_id=${client_id}`
    let response = await fetch(URLWithParm);

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}. client_id=${client_id}`);
    }
    else {
        if(type === 'blob') {
            content = await response.blob();
        } else if(type === 'text') {
            content = await response.text();
        }
    }
    return content;
}
 
const run_test_cloud_function = async (totalClients, broker, channel) => {
  const clientIds = [...Array(totalClients).keys()].map(clientIds => clientIds + 1)
  console.log(clientIds)
  try {
        const CustomRetry = (e, attemptNumber) => {
            console.log("e", e)
            console.log("attempt", attemptNumber)
            return true;
        }
        const options = {
            startingDelay: 2000,
            jitter: "full",
            retry: CustomRetry
        }
        const responses = clientIds.map(clientId => backOff(() => callClient(broker, clientId, channel), options));
        const results = await Promise.all(responses);
        console.log(results)
  } catch (e) {
    // handle error
    console.log("Error:", e)
  }
}
 
const totalClients = 50;
const channel = "gRPC"
const broker = "35.203.161.106:8081"
run_test_cloud_function(totalClients, broker, channel);