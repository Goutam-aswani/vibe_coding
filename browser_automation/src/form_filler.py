import asyncio
import logging
import os
from typing import List, Dict, Any
from pathlib import Path
from playwright.async_api import Page
from src.models import FieldAnswer, FieldType

logger = logging.getLogger(__name__)


class FormFiller:
    """Fills form fields and submits the application"""
    
    def __init__(self, page: Page):
        self.page = page
        self.resume_path = os.getenv("RESUME_PATH", "./documents/resume.pdf")
        self.cover_letter_path = os.getenv("COVER_LETTER_PATH", "./documents/cover_letter.pdf")
    
    async def fill_field(self, field_answer: FieldAnswer, field_info: Dict[str, Any]) -> bool:
        """Fill a single field with the provided answer"""
        try:
            field_id = field_answer.field_id
            value = field_answer.value
            field_type = field_info.get('type', 'text')
            
            logger.info(f"Filling field {field_id} with value: {value}")
            
            if field_type == FieldType.TEXT or field_type == FieldType.EMAIL or \
               field_type == FieldType.PHONE or field_type == FieldType.NUMBER:
                return await self._fill_text_input(field_id, str(value))
            
            elif field_type == FieldType.TEXTAREA:
                return await self._fill_textarea(field_id, str(value))
            
            elif field_type == FieldType.SELECT:
                return await self._fill_select(field_id, str(value))
            
            elif field_type == FieldType.RADIO:
                return await self._fill_radio(field_id, str(value))
            
            elif field_type == FieldType.CHECKBOX:
                return await self._fill_checkbox(field_id, value)
            
            elif field_type == FieldType.FILE:
                return await self._upload_file(field_id, str(value))
            
            else:
                logger.warning(f"Unknown field type: {field_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error filling field {field_answer.field_id}: {e}")
            return False
    
    async def _fill_text_input(self, field_id: str, value: str) -> bool:
        """Fill a text input field"""
        try:
            # Try to find by ID first
            input_elem = await self.page.locator(f'#{field_id}').first
            
            # Clear existing value
            await input_elem.clear()
            await asyncio.sleep(0.2)
            
            # Type the value with human-like delay
            await input_elem.type(value, delay=50)
            await asyncio.sleep(0.3)
            
            logger.info(f"Filled text input {field_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error filling text input {field_id}: {e}")
            return False
    
    async def _fill_textarea(self, field_id: str, value: str) -> bool:
        """Fill a textarea field"""
        try:
            textarea = await self.page.locator(f'#{field_id}').first
            
            await textarea.clear()
            await asyncio.sleep(0.2)
            
            await textarea.type(value, delay=30)
            await asyncio.sleep(0.3)
            
            logger.info(f"Filled textarea {field_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error filling textarea {field_id}: {e}")
            return False
    
    async def _fill_select(self, field_id: str, value: str) -> bool:
        """Fill a select/dropdown field"""
        try:
            select = await self.page.locator(f'#{field_id}').first
            
            # Try to select by visible text first
            try:
                await select.select_option(label=value, timeout=2000)
                logger.info(f"Filled select {field_id} with label: {value}")
                return True
            except:
                # Try to select by value
                try:
                    await select.select_option(value=value, timeout=2000)
                    logger.info(f"Filled select {field_id} with value: {value}")
                    return True
                except:
                    # Try to find closest match
                    options = await select.locator('option').all()
                    for option in options:
                        option_text = await option.text_content()
                        if option_text and value.lower() in option_text.lower():
                            option_value = await option.get_attribute('value')
                            await select.select_option(value=option_value)
                            logger.info(f"Filled select {field_id} with closest match: {option_text}")
                            return True
            
            logger.warning(f"Could not find matching option for {field_id}: {value}")
            return False
            
        except Exception as e:
            logger.error(f"Error filling select {field_id}: {e}")
            return False
    
    async def _fill_radio(self, group_name: str, value: str) -> bool:
        """Fill a radio button group"""
        try:
            # Find all radio buttons in the group
            radios = await self.page.locator(f'input[type="radio"][name="{group_name}"]').all()
            
            for radio in radios:
                # Get the label for this radio
                radio_id = await radio.get_attribute('id')
                radio_value = await radio.get_attribute('value')
                
                label_text = radio_value
                if radio_id:
                    try:
                        label = await self.page.locator(f'label[for="{radio_id}"]').first.text_content(timeout=1000)
                        if label:
                            label_text = label.strip()
                    except:
                        pass
                
                # Check if this is the radio we want to select
                if value.lower() in label_text.lower() or value.lower() == radio_value.lower():
                    await radio.check()
                    await asyncio.sleep(0.3)
                    logger.info(f"Selected radio {group_name}: {label_text}")
                    return True
            
            logger.warning(f"Could not find matching radio option for {group_name}: {value}")
            return False
            
        except Exception as e:
            logger.error(f"Error filling radio {group_name}: {e}")
            return False
    
    async def _fill_checkbox(self, field_id: str, value: Any) -> bool:
        """Fill a checkbox field"""
        try:
            checkbox = await self.page.locator(f'#{field_id}').first
            
            # Determine if we should check or uncheck
            should_check = False
            if isinstance(value, bool):
                should_check = value
            elif isinstance(value, str):
                should_check = value.lower() in ['true', 'yes', 'checked', '1']
            
            is_checked = await checkbox.is_checked()
            
            if should_check and not is_checked:
                await checkbox.check()
                logger.info(f"Checked checkbox {field_id}")
            elif not should_check and is_checked:
                await checkbox.uncheck()
                logger.info(f"Unchecked checkbox {field_id}")
            
            await asyncio.sleep(0.3)
            return True
            
        except Exception as e:
            logger.error(f"Error filling checkbox {field_id}: {e}")
            return False
    
    async def _upload_file(self, field_id: str, file_path: str) -> bool:
        """Upload a file"""
        try:
            # If file_path is 'resume' or 'cover_letter', use predefined paths
            if file_path.lower() == 'resume':
                file_path = self.resume_path
            elif file_path.lower() == 'cover_letter' or file_path.lower() == 'coverletter':
                file_path = self.cover_letter_path
            
            # Check if file exists
            if not Path(file_path).exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            file_input = await self.page.locator(f'#{field_id}').first
            await file_input.set_input_files(file_path)
            await asyncio.sleep(1)
            
            logger.info(f"Uploaded file {file_path} to {field_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file to {field_id}: {e}")
            return False
    
    async def click_next(self) -> bool:
        """Click the Next/Continue button"""
        try:
            # Try multiple selectors for Next button
            selectors = [
                'button[aria-label*="Continue"]',
                'button[aria-label*="next step"]',
                'button:has-text("Next")',
                'button:has-text("Continue")',
                '.jobs-easy-apply-modal footer button[data-easy-apply-next-button]'
            ]
            
            for selector in selectors:
                try:
                    button = await self.page.locator(selector).first
                    if await button.is_visible(timeout=1000):
                        await button.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await button.click()
                        await asyncio.sleep(2)
                        logger.info("Clicked Next button")
                        return True
                except:
                    continue
            
            logger.warning("Next button not found")
            return False
            
        except Exception as e:
            logger.error(f"Error clicking Next: {e}")
            return False
    
    async def click_review(self) -> bool:
        """Click the Review button"""
        try:
            selectors = [
                'button[aria-label*="Review"]',
                'button:has-text("Review")',
                'button:has-text("Review application")'
            ]
            
            for selector in selectors:
                try:
                    button = await self.page.locator(selector).first
                    if await button.is_visible(timeout=1000):
                        await button.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await button.click()
                        await asyncio.sleep(2)
                        logger.info("Clicked Review button")
                        return True
                except:
                    continue
            
            logger.warning("Review button not found")
            return False
            
        except Exception as e:
            logger.error(f"Error clicking Review: {e}")
            return False
    
    async def submit_application(self) -> bool:
        """Submit the final application"""
        try:
            selectors = [
                'button[aria-label*="Submit application"]',
                'button:has-text("Submit application")',
                'button:has-text("Submit")',
                '.jobs-easy-apply-modal footer button[type="submit"]'
            ]
            
            for selector in selectors:
                try:
                    button = await self.page.locator(selector).first
                    if await button.is_visible(timeout=2000):
                        await button.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await button.click()
                        await asyncio.sleep(3)
                        logger.info("Clicked Submit button")
                        return True
                except:
                    continue
            
            logger.error("Submit button not found")
            return False
            
        except Exception as e:
            logger.error(f"Error submitting application: {e}")
            return False
    
    async def check_success(self) -> bool:
        """Check if application was submitted successfully"""
        try:
            # Wait a bit for success message
            await asyncio.sleep(2)
            
            # Look for success indicators
            success_selectors = [
                'text="Your application was sent"',
                'text="Application submitted"',
                'text="successfully"',
                '[class*="success"]',
                '[aria-label*="success"]'
            ]
            
            for selector in success_selectors:
                try:
                    element = await self.page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        logger.info("Application success confirmed")
                        return True
                except:
                    continue
            
            # If modal is closed, also consider it success
            try:
                modal = await self.page.locator('.jobs-easy-apply-modal').first
                is_visible = await modal.is_visible(timeout=2000)
                if not is_visible:
                    logger.info("Modal closed - assuming success")
                    return True
            except:
                logger.info("Modal not found - assuming success")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking success: {e}")
            return False
    
    async def close_modal(self) -> bool:
        """Close the Easy Apply modal"""
        try:
            # Look for close button
            close_selectors = [
                'button[aria-label*="Dismiss"]',
                'button[aria-label*="Close"]',
                '.jobs-easy-apply-modal button[data-test-modal-close-btn]',
                '.artdeco-modal__dismiss'
            ]
            
            for selector in close_selectors:
                try:
                    button = await self.page.locator(selector).first
                    if await button.is_visible(timeout=1000):
                        await button.click()
                        await asyncio.sleep(1)
                        logger.info("Closed modal")
                        return True
                except:
                    continue
            
            # Press Escape key as fallback
            await self.page.keyboard.press('Escape')
            await asyncio.sleep(1)
            logger.info("Closed modal with Escape")
            return True
            
        except Exception as e:
            logger.error(f"Error closing modal: {e}")
            return False
