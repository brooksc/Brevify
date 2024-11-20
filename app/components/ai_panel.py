"""AI service options panel component."""

from fasthtml import Component, Div, Button, Select, Option
from ..services.ai_service import AIService, AIServiceType

class AIOptionsPanel(Component):
    """Panel for AI service options and controls."""
    
    def __init__(self, ai_service: AIService):
        """Initialize the AI options panel."""
        self.ai_service = ai_service

    def render(self):
        """Render the AI options panel."""
        return Div(
            {"class": "bg-white p-4 rounded-lg shadow-md"},
            
            # Service selection
            Div(
                {"class": "mb-4"},
                Select(
                    {"class": "w-full p-2 border rounded",
                     "name": "ai_service",
                     "hx-post": "/update-service",
                     "hx-trigger": "change",
                     "hx-target": "#template-options"},
                    *[Option({"value": service.value}, service.value.title())
                      for service in AIServiceType]
                )
            ),
            
            # Template selection
            Div(
                {"id": "template-options", "class": "mb-4"},
                Select(
                    {"class": "w-full p-2 border rounded",
                     "name": "template",
                     "hx-post": "/update-template",
                     "hx-trigger": "change",
                     "hx-target": "#template-description"},
                    *[Option({"value": name}, 
                            template.description)
                      for name, template in self.ai_service.templates.items()]
                )
            ),
            
            # Template description
            Div(
                {"id": "template-description",
                 "class": "text-sm text-gray-600 mb-4"},
                "Select a template to see its description"
            ),
            
            # Action buttons
            Div(
                {"class": "flex space-x-2"},
                Button(
                    {"class": "bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600",
                     "hx-post": "/process-ai",
                     "hx-target": "#results"},
                    "Process with AI"
                ),
                Button(
                    {"class": "border border-blue-500 text-blue-500 px-4 py-2 rounded hover:bg-blue-50",
                     "hx-post": "/launch-ai",
                     "hx-target": "none"},
                    "Open in New Tab"
                )
            )
        )
