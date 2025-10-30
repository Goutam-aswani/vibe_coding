# Test Script for LinkedIn Automation

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000"
TEST_JOB_URL = "https://www.linkedin.com/jobs/view/4308463479/"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_start_application(job_url):
    """Test starting an application"""
    print(f"\n🚀 Starting application for: {job_url}")
    
    response = requests.post(
        f"{API_URL}/start-application",
        json={"job_url": job_url}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Application started!")
        print(f"Session ID: {data['session_id']}")
        print(f"Job Title: {data.get('job_title', 'N/A')}")
        print(f"Company: {data.get('company_name', 'N/A')}")
        print(f"Status: {data['status']}")
        
        if data.get('current_step'):
            step = data['current_step']
            print(f"\nStep {step['step_number']}: {step.get('step_title', 'N/A')}")
            print(f"Fields to fill: {len(step['fields'])}")
            print("\nFields:")
            for field in step['fields']:
                print(f"  - {field['label']} ({field['field_type']}) [{'Required' if field.get('required') else 'Optional'}]")
                if field.get('options'):
                    print(f"    Options: {', '.join(field['options'][:3])}...")
        
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_submit_application(session_id, answers):
    """Test submitting application answers"""
    print(f"\n📝 Submitting answers for session: {session_id}")
    
    response = requests.post(
        f"{API_URL}/submit-application",
        json={
            "session_id": session_id,
            "answers": answers,
            "continue_to_next": True
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Submission successful!")
        print(f"Status: {data['status']}")
        print(f"Message: {data['message']}")
        
        if data.get('current_step'):
            step = data['current_step']
            print(f"\nNext Step {step['step_number']}: {step.get('step_title', 'N/A')}")
            print(f"Fields to fill: {len(step['fields'])}")
        
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_list_sessions():
    """Test listing active sessions"""
    print("\n📋 Listing active sessions...")
    
    response = requests.get(f"{API_URL}/sessions")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Active sessions: {data['active_sessions']}")
        for session in data['sessions']:
            print(f"  - {session['session_id']}: {session['job_title']} at {session['company_name']} (Step {session['current_step']})")
        return data
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_cancel_session(session_id):
    """Test canceling a session"""
    print(f"\n🚫 Canceling session: {session_id}")
    
    response = requests.delete(f"{API_URL}/session/{session_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Session cancelled")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def generate_mock_answers(fields):
    """Generate mock answers for testing"""
    answers = []
    
    for field in fields:
        field_type = field['field_type']
        field_id = field['field_id']
        
        if field_type == 'text':
            answers.append({"field_id": field_id, "value": "Test Value"})
        elif field_type == 'email':
            answers.append({"field_id": field_id, "value": "test@example.com"})
        elif field_type == 'phone':
            answers.append({"field_id": field_id, "value": "+1234567890"})
        elif field_type == 'number':
            answers.append({"field_id": field_id, "value": "5"})
        elif field_type == 'textarea':
            answers.append({"field_id": field_id, "value": "This is a test response."})
        elif field_type == 'select' and field.get('options'):
            answers.append({"field_id": field_id, "value": field['options'][0]})
        elif field_type == 'radio' and field.get('options'):
            answers.append({"field_id": field_id, "value": field['options'][0]})
        elif field_type == 'checkbox':
            answers.append({"field_id": field_id, "value": True})
        elif field_type == 'file':
            answers.append({"field_id": field_id, "value": "resume"})
    
    return answers

def run_full_test():
    """Run complete test flow"""
    print("=" * 60)
    print("LinkedIn Automation - Full Test")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Is the service running?")
        return
    
    # Test 2: List sessions (should be empty)
    test_list_sessions()
    
    # Test 3: Start application
    print("\n⚠️  WARNING: This will actually navigate to the job and click Easy Apply!")
    print("Make sure you're logged in to LinkedIn and ready to test.")
    
    confirm = input("\nProceed with test? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Test cancelled.")
        return
    
    app_data = test_start_application(TEST_JOB_URL)
    
    if not app_data or app_data['status'] == 'failed':
        print("\n❌ Could not start application. Check the error above.")
        return
    
    session_id = app_data['session_id']
    
    # Test 4: List sessions (should show our session)
    test_list_sessions()
    
    # Test 5: Check if we need to submit answers
    if app_data.get('current_step') and app_data['status'] == 'waiting_for_input':
        fields = app_data['current_step']['fields']
        
        print("\n🤖 Generating mock answers...")
        answers = generate_mock_answers(fields)
        
        print(f"Generated {len(answers)} answers:")
        for ans in answers:
            print(f"  - {ans['field_id']}: {ans['value']}")
        
        confirm_submit = input("\nSubmit these answers? (yes/no): ")
        if confirm_submit.lower() == 'yes':
            submit_data = test_submit_application(session_id, answers)
            
            # Keep submitting if there are more steps
            while submit_data and submit_data['status'] == 'waiting_for_input':
                print("\n⏩ More steps detected...")
                time.sleep(2)
                
                fields = submit_data['current_step']['fields']
                answers = generate_mock_answers(fields)
                
                print(f"Generated {len(answers)} answers for step {submit_data['current_step']['step_number']}")
                
                confirm_continue = input("Continue to next step? (yes/no): ")
                if confirm_continue.lower() != 'yes':
                    print("Stopping. Session is still active.")
                    break
                
                submit_data = test_submit_application(session_id, answers)
            
            if submit_data and submit_data['status'] == 'completed':
                print("\n🎉 Application completed successfully!")
        else:
            print("\n⚠️  Submission cancelled. Session is still active.")
            test_cancel_session(session_id)
    
    # Final session list
    test_list_sessions()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    print("\n📸 Check the 'screenshots' folder for captured images")
    print("📋 Check the terminal output for detailed logs")

if __name__ == "__main__":
    run_full_test()
