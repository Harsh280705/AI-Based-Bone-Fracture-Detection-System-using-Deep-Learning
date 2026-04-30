import os
import customtkinter as ctk
import pyautogui
import pygetwindow
from tkinter import filedialog
from PIL import ImageTk, Image
from predictions import predict
import threading

# Suppress TensorFlow verbose output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logging (0=all, 1=info, 2=warning, 3=error)
try:
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')  # Set TensorFlow logger to ERROR level only
except:
    pass

# Color scheme - Medical/AI theme
COLOR_BG_MAIN = "#0F1419"          # Deep dark blue-black
COLOR_BG_SECONDARY = "#1A1F2E"     # Slightly lighter dark blue
COLOR_CARD_BG = "#242E3F"          # Card background
COLOR_PRIMARY = "#0EA5E9"          # Medical blue
COLOR_PRIMARY_HOVER = "#0284C7"    # Darker medical blue
COLOR_SUCCESS = "#10B981"          # Green for normal
COLOR_DANGER = "#EF4444"           # Red for fractured
COLOR_TEXT_PRIMARY = "#FFFFFF"     # White text
COLOR_TEXT_SECONDARY = "#A0AEC0"   # Light gray text
COLOR_BORDER = "#3A4556"           # Border color

# global variables
project_folder = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(project_folder, "images")

filename = ""

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Bone Fracture Detection System")
        self.geometry("700x850")  # Reduced from 1000 to fit all on screen
        self.configure(fg_color=COLOR_BG_MAIN)
        
        # Set window icon if available
        try:
            self.iconbitmap(os.path.join(folder_path, "info.png"))
        except:
            pass
        
        # Main scrollable container
        self.main_container = ctk.CTkFrame(master=self, fg_color=COLOR_BG_MAIN)
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create header section
        self._create_header()
        
        # Create upload card
        self._create_upload_section()
        
        # Create preview card
        self._create_preview_section()
        
        # Create controls card
        self._create_controls_section()
        
        # Create results card
        self._create_results_section()
        
        # Store current image for display
        self.current_image = None
        self.is_predicting = False

    def _create_header(self):
        """Create the header section with title and info button"""
        header_frame = ctk.CTkFrame(master=self.main_container, fg_color=COLOR_BG_SECONDARY, height=75)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title section
        title_container = ctk.CTkFrame(master=header_frame, fg_color=COLOR_BG_SECONDARY)
        title_container.pack(fill="both", expand=True, padx=25, pady=12)
        
        title_label = ctk.CTkLabel(
            master=title_container,
            text="🔍 Bone Fracture Detection",
            font=ctk.CTkFont("Segoe UI", 24, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            master=title_container,
            text="AI-Powered Medical Imaging Analysis",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Info button in header
        try:
            img1 = ctk.CTkImage(Image.open(os.path.join(folder_path, "info.png")), size=(24, 24))
            info_btn = ctk.CTkButton(
                master=title_container,
                text="",
                image=img1,
                command=self.open_image_window,
                width=40,
                height=40,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                corner_radius=8
            )
            info_btn.pack(side="right", padx=(10, 0))
        except:
            info_btn = ctk.CTkButton(
                master=title_container,
                text="ℹ️ Info",
                command=self.open_image_window,
                width=60,
                height=36,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                corner_radius=8,
                font=ctk.CTkFont("Segoe UI", 11, "bold")
            )
            info_btn.pack(side="right", padx=(10, 0))

    def _create_upload_section(self):
        """Create the upload section card"""
        card = self._create_card("📤 Upload X-Ray Image")
        
        upload_container = ctk.CTkFrame(master=card, fg_color=COLOR_CARD_BG)
        upload_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.upload_btn = ctk.CTkButton(
            master=upload_container,
            text="Choose Image File",
            command=self.upload_image,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            height=38,
            corner_radius=8
        )
        self.upload_btn.pack(fill="x", pady=(0, 8))
        
        info_text = ctk.CTkLabel(
            master=upload_container,
            text="PNG, JPG, JPEG • Processed at 224×224 pixels",
            font=ctk.CTkFont("Segoe UI", 9),
            text_color=COLOR_TEXT_SECONDARY,
            justify="center"
        )
        info_text.pack()

    def _create_preview_section(self):
        """Create the image preview card"""
        card = self._create_card("🖼️ Image Preview")
        
        preview_container = ctk.CTkFrame(master=card, fg_color=COLOR_CARD_BG)
        preview_container.pack(fill="both", expand=True, padx=15, pady=8)
        
        # Create frame for image - REDUCED SIZE
        self.frame2 = ctk.CTkFrame(
            master=preview_container,
            fg_color=COLOR_BG_SECONDARY,
            width=200,
            height=200,
            corner_radius=12,
            border_width=2,
            border_color=COLOR_BORDER
        )
        self.frame2.pack(pady=5)
        self.frame2.pack_propagate(False)
        
        # Default placeholder image
        try:
            img = Image.open(os.path.join(folder_path, "Abstract.jpg"))
        except:
            # Create a simple placeholder if image not found
            img = Image.new('RGB', (200, 200), color=COLOR_BG_SECONDARY)
        
        img_resized = img.resize((200, 200))
        img = ImageTk.PhotoImage(img_resized)
        
        self.img_label = ctk.CTkLabel(master=self.frame2, text="", image=img)
        self.img_label.pack()
        self.img_label.image = img  # Keep reference

    def _create_controls_section(self):
        """Create the prediction controls card"""
        card = self._create_card("⚙️ Analysis")
        
        controls_container = ctk.CTkFrame(master=card, fg_color=COLOR_CARD_BG)
        controls_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        button_container = ctk.CTkFrame(master=controls_container, fg_color=COLOR_CARD_BG)
        button_container.pack(fill="x", pady=3)
        
        self.predict_btn = ctk.CTkButton(
            master=button_container,
            text="🔬 Analyze Image",
            command=self.predict_gui,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            height=38,
            corner_radius=8
        )
        self.predict_btn.pack(fill="x")
        
        # Loading indicator label
        self.loading_label = ctk.CTkLabel(
            master=controls_container,
            text="",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=COLOR_PRIMARY
        )
        self.loading_label.pack(pady=3)

    def _create_results_section(self):
        """Create the results display card"""
        card = self._create_card("📋 Analysis Results")
        
        self.result_frame = ctk.CTkFrame(master=card, fg_color=COLOR_CARD_BG)
        self.result_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Body part type result
        self.res1_label = ctk.CTkLabel(
            master=self.result_frame,
            text="",
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont("Segoe UI", 11),
            wraplength=600
        )
        self.res1_label.pack(pady=(3, 8), fill="both", expand=False, anchor="w")
        
        # Fracture status result
        self.res2_label = ctk.CTkLabel(
            master=self.result_frame,
            text="",
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
            wraplength=600
        )
        self.res2_label.pack(pady=(0, 10), fill="both", expand=False, anchor="w")
        
        # Save button
        self.save_btn = ctk.CTkButton(
            master=self.result_frame,
            text="💾 Save Result",
            command=self.save_result,
            fg_color="#6B7280",
            hover_color="#4B5563",
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            height=35,
            corner_radius=8
        )
        # Don't pack initially
        
        # Save confirmation label
        self.save_label = ctk.CTkLabel(
            master=self.result_frame,
            text="",
            text_color=COLOR_SUCCESS,
            font=ctk.CTkFont("Segoe UI", 10, "bold")
        )

    def _create_card(self, title):
        """Helper function to create a card-style container"""
        card = ctk.CTkFrame(
            master=self.main_container,
            fg_color=COLOR_BG_SECONDARY,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER
        )
        card.pack(fill="x", padx=15, pady=8)
        
        # Card header
        header = ctk.CTkLabel(
            master=card,
            text=title,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        header.pack(anchor="w", padx=15, pady=(10, 0))
        
        # Divider
        divider = ctk.CTkFrame(master=card, fg_color=COLOR_BORDER, height=1)
        divider.pack(fill="x", padx=15, pady=(8, 0))
        
        return card

    def upload_image(self):
        """Handle image upload with preview"""
        global filename
        f_types = [("Image Files", "*.png *.jpg *.jpeg"), ("All Files", "*.*")]
        filename = filedialog.askopenfilename(filetypes=f_types, initialdir=folder_path)
        
        if filename:
            # Clear previous results
            self.res2_label.configure(text="")
            self.res1_label.configure(text="")
            self.save_btn.pack_forget()
            self.save_label.pack_forget()
            self.save_label.configure(text="")
            self.loading_label.configure(text="")
            
            try:
                # Load and display image
                img = Image.open(filename)
                img_resized = img.resize((200, 200))
                img_tk = ImageTk.PhotoImage(img_resized)
                
                self.img_label.configure(image=img_tk, text="")
                self.img_label.image = img_tk
                self.current_image = img_tk
            except Exception as e:
                self.res2_label.configure(
                    text=f"❌ Error loading image: {str(e)[:50]}",
                    text_color=COLOR_DANGER
                )

    def predict_gui(self):
        """Handle prediction with loading indicator"""
        global filename
        
        if not filename:
            self.res2_label.configure(
                text="⚠️ Please upload an image first",
                text_color=COLOR_TEXT_SECONDARY
            )
            return
        
        if self.is_predicting:
            return
        
        # Clear previous results
        self.res1_label.configure(text="")
        self.res2_label.configure(text="")
        self.save_label.configure(text="")
        
        # Disable button and show loading
        self.is_predicting = True
        self.predict_btn.configure(state="disabled", text="🔄 Analyzing...")
        self.loading_label.configure(text="Processing, please wait...")
        self.update()
        self.update_idletasks()
        
        # Run prediction in separate thread to keep UI responsive
        def run_prediction():
            bone_type_result = None
            result = None
            error_msg = None
            
            try:
                print("Starting prediction...")
                # CRITICAL: Do not modify prediction calls or return values
                bone_type_result = predict(filename)
                print(f"Bone type result: {bone_type_result}")
                
                result = predict(filename, bone_type_result)
                print(f"Fracture result: {result}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"Prediction Error: {error_msg}")
            
            finally:
                # Always restore UI state
                self.is_predicting = False
                self.predict_btn.configure(state="normal", text="🔬 Analyze Image")
                self.loading_label.configure(text="")
                
                # Update GUI on main thread with proper timing
                if error_msg:
                    self.after(50, lambda: self._display_error(error_msg))
                else:
                    self.after(50, lambda: self._display_results(bone_type_result, result))
        
        thread = threading.Thread(target=run_prediction, daemon=True)
        thread.start()

    def _display_results(self, bone_type_result, result):
        """Display prediction results with color coding"""
        print(f"Displaying results: bone_type={bone_type_result}, result={result}")
        
        if not bone_type_result or not result:
            print("Error: Missing results data!")
            return
        
        try:
            # Clear previous states
            self.save_label.configure(text="")
            
            # Display bone type
            self.res1_label.configure(
                text=f"🦴 Bone Type: {bone_type_result}",
                text_color=COLOR_PRIMARY
            )
            self.res1_label.update_idletasks()
            
            # Display fracture status with color coding
            if result == 'fractured':
                emoji = "⚠️"
                status_text = "Fracture Detected"
                color = COLOR_DANGER
            else:
                emoji = "✅"
                status_text = "No Fracture"
                color = COLOR_SUCCESS
            
            self.res2_label.configure(
                text=f"{emoji} {status_text}",
                text_color=color,
                font=ctk.CTkFont("Segoe UI", 18, "bold")
            )
            self.res2_label.update_idletasks()
            
            # Show save button if not already visible
            if not self.save_btn.winfo_ismapped():
                self.save_btn.pack(fill="x", pady=(8, 8))
                self.save_label.pack(pady=(3, 0))
            
            # Force GUI refresh
            self.update()
            self.update_idletasks()
            
            print("Results displayed successfully!")
        except Exception as e:
            print(f"Error displaying results: {e}")
            import traceback
            traceback.print_exc()

    def _display_error(self, error_msg):
        """Display error message"""
        print(f"Displaying error: {error_msg}")
        try:
            self.res2_label.configure(
                text=f"❌ Error: {error_msg[:60]}",
                text_color=COLOR_DANGER
            )
            self.res2_label.update_idletasks()
            
            self.res1_label.configure(text="")
            self.res1_label.update_idletasks()
            
            self.update()
            self.update_idletasks()
        except Exception as e:
            print(f"Error displaying error: {e}")

    def save_result(self):
        """Save the prediction result as screenshot"""
        tempdir = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            initialdir=os.path.join(project_folder, 'PredictResults/')
        )
        
        if tempdir:
            try:
                window = pygetwindow.getWindowsWithTitle('Bone Fracture Detection')[0]
                screenshot = pyautogui.screenshot()
                screenshot.save(tempdir)
                self.save_label.configure(
                    text_color=COLOR_SUCCESS,
                    text="✅ Result saved successfully!"
                )
            except Exception as e:
                self.save_label.configure(
                    text_color=COLOR_DANGER,
                    text=f"❌ Save failed: {str(e)[:30]}"
                )

    def open_image_window(self):
        """Open rules/guidelines image"""
        try:
            im = Image.open(os.path.join(folder_path, "rules.jpeg"))
            im = im.resize((700, 700))
            im.show()
        except Exception as e:
            print(f"Could not open rules image: {e}")


# Initialize and run the application
if __name__ == "__main__":
    app = App()
    app.mainloop()
