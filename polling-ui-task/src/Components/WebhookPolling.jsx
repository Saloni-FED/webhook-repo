import { useState, useEffect } from "react"

const WebhookPolling = () => {
    const [events, setEvents] = useState([])

    useEffect(() => {
      // Function to fetch events from MongoDB
      const fetchEvents = async () => {
        try {
          const response = await fetch(import.meta.env.VITE_API_URL)
          if (!response.ok) {
              throw new Error();
            }
          const data = await response.json()
          console.log(data)
          setEvents(data)
        } catch (error) {
          console.error('Error fetching events:', error)
        }
      }
  
      // Initial fetch
      fetchEvents()
  
      // Set up polling every 15 seconds
      const interval = setInterval(fetchEvents, 15000)
  
      // Cleanup interval on unmount
      return () => clearInterval(interval)
    }, [])
  
    return (
      <div className="container mx-auto p-4">
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <div className="bg-gray-800 text-white p-4">
            <h2 className="text-xl font-semibold">GitHub Webhook Events</h2>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              {events.map((event, index) => (
                <div key={index} className="border rounded p-4 bg-gray-100">
                  <div className="flex justify-between items-start">
                    <span className="font-medium text-sm">{event.type}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(event.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="mt-2 text-sm">{event.message}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
}

export default WebhookPolling