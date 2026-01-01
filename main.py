import os
from typing import List
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI()

# 1. Enable CORS (Crucial for Frontend-Backend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace "*" with your actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Setup Directories
# Ensure these folders exist in your project root!
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("templates"):
    os.makedirs("templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 3. Initialize Gemini Client
# Use your key directly or via os.getenv
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# 4. Data Models
class ReviewRequest(BaseModel):
    name: str
    traits: List[str]

# 5. Routes
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-review")
async def generate_review(request: ReviewRequest):
    # Prepare the traits string
    traits_str = ", ".join(request.traits) if request.traits else "general great experience"
    
    # Create a descriptive prompt for the AI
    prompt = (
        
        f"""Write a positive, authentic-sounding Google review for a cafe named '{request.name}'. 
        The review should be enthusiastic, around 60-70 words long, and incorporate the following themes: {traits_str}.
        Dont mention any specific food or drink items.
        Paraphrase and include these sentences in the review naturally and randomly" "Service by Shehnaz was exceptional" "Drinks made by Tausif were refreshing and top-notch" 
        
        Please introduce some common, natural-sounding spelling mistakes to make it sound more like a real, casual user review. 
        For example, 'atmosphere' could be 'atmospher', 'amazing' could be 'amazin'. Keep the tone natural and personal. 
        Do not include any special characters like asterisks (*) or emojis for decoration. Use very less punctations and exlamation marks, infact use only one exclamation mark. Write informally. And strictly no Emojis."""
    )

    try:
        # Call the Gemini 2.0 Flash model
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        # Extract the text content from the response
        generated_text = response.text.strip()
        
        return {"review": generated_text}
        
    except Exception as e:
        # Detailed error logging
        print(f"Gemini API Error: {e}")
        return {"review": f"Error generating review: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)