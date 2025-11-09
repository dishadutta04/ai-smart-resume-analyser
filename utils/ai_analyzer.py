from openai import OpenAI
import google.generativeai as genai
import json

def analyze_resume(resume_text, job_description, api_key, provider, model):
    """Analyze resume and return structured feedback in JSON format."""

    prompt = f"""
    Analyze this resume and provide detailed feedback in JSON format.

    Resume:
    {resume_text}
    {"Job Description: " + job_description if job_description else ""}

    Provide analysis in this JSON format:
    {{
      "ats_score": <0-100>,
      "summary": "<brief overview>",
      "strengths": ["strength1", "strength2", ...],
      "weaknesses": ["weakness1", "weakness2", ...],
      "suggestions": [
        {{"title": "suggestion title", "description": "detailed description"}},
        ...
      ],
      "keywords": {{
        "found": ["keyword1", "keyword2"],
        "missing": ["keyword3", "keyword4"]
      }}
    }}

    Return ONLY valid JSON, no markdown or extra text.
    """

    try:
        if provider == "OpenAI":
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer and ATS specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            result = response.choices[0].message.content
        else:
            genai.configure(api_key=api_key)
            ai_model = genai.GenerativeModel(model)
            response = ai_model.generate_content(prompt)
            result = response.text

        # Clean the response
        result = result.strip()
        if result.startswith('```json'):
            result = result[7:]
        elif result.startswith('```'):
            result = result[3:]
        if result.endswith('```'):
            result = result[:-3]

        # Parse JSON
        return json.loads(result)

    except json.JSONDecodeError as e:
        return {
            "ats_score": 50,
            "summary": "Analysis completed with some limitations.",
            "strengths": ["Resume uploaded successfully"],
            "weaknesses": ["Error in JSON parsing", str(e)],
            "suggestions": [{"title": "Review manually", "description": "The AI response was not valid JSON."}],
            "keywords": {"found": [], "missing": []}
        }
    except Exception as e:
        return {
            "ats_score": 50,
            "summary": "Analysis completed with some limitations.",
            "strengths": ["Resume uploaded successfully"],
            "weaknesses": ["Error in detailed analysis", str(e)],
            "suggestions": [{"title": "Review manually", "description": str(e)}],
            "keywords": {"found": [], "missing": []}
        }

def improve_resume(resume_text, analysis, job_description, api_key, provider, model):
    """Generate an improved version of the resume based on analysis."""

    prompt = f"""
    Rewrite this resume to improve it based on the analysis provided.

    Original Resume:
    {resume_text}

    Analysis:
    {json.dumps(analysis, indent=2)}

    {"Target Job: " + job_description if job_description else ""}

    Rewrite the resume to:
    1. Address all weaknesses mentioned
    2. Incorporate missing keywords naturally
    3. Enhance strengths
    4. Make it ATS-friendly
    5. Keep the same format and structure

    Return the improved resume text only, no explanations or markdown.
    """

    try:
        if provider == "OpenAI":
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        else:
            genai.configure(api_key=api_key)
            ai_model = genai.GenerativeModel(model)
            response = ai_model.generate_content(prompt)
            return response.text

    except Exception as e:
        return f"Error generating improved resume: {str(e)}"
