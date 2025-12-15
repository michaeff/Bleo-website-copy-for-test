import os
from flask import Flask, render_template, abort, url_for, send_file

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/tilescans')
def tilescans():
    return render_template('tilescans.html')

@app.route('/week/<int:week>')
def week_detail(week):
    # Check if the week exists by looking for the 3d_images folder
    base = os.path.join(app.static_folder, '3d_images', f'week{week}')
    if not os.path.isdir(base):
        abort(404)
    
    return render_template('week_detail.html', week=week)

@app.route('/download/week<int:week>')
# def download_week(week):
#     # Path to the CZI file
#     czi_path = os.path.join(app.static_folder, 'czi_images', f'week{week}.czi')
    
#     # Check if file exists
#     if not os.path.isfile(czi_path):
#         abort(404)
    
#     # Send the file as download
#     return send_file(czi_path, as_attachment=True, download_name=f'week{week}.czi')

def download_week(week):
    # Path to the CZI file
    czi_path = os.path.join('https://media.githubusercontent.com/media/michaeff/Bleo-website/refs/heads/main/static/', 'czi_images', f'week{week}.czi')
    
    # Check if file exists
    if not os.path.isfile(czi_path):
        abort(404)
    
    # Send the file as download
    return send_file(czi_path, as_attachment=True, download_name=f'week{week}.czi')

@app.route('/download/weektif<int:week>')
def download_weektif(week):
    # Path to the CZI file
    czi_path = os.path.join(app.static_folder, 'czi_images', f'week{week}.tif')
    
    # Check if file exists
    if not os.path.isfile(czi_path):
        abort(404)
    
    # Send the file as download
    return send_file(czi_path, as_attachment=True, download_name=f'week{week}.tif')

@app.route('/download/detailweek<string:week>')
def download_detailweek(week):
    # Path to the CZI file
    week0= week[0]
    if week0 == '0':
        czi_path = os.path.join(app.static_folder, 'czi_images_detailed',f'week{week0}', f'week{week0}.czi')
        # Check if file exists
        print(czi_path)
        if not os.path.isfile(czi_path):
            abort(404)
        
        # Send the file as download
        return send_file(czi_path, as_attachment=True, download_name=f'detailweek{week0}.czi')
    else:
        weekrest= week[1:]

        czi_path = os.path.join(app.static_folder, 'czi_images_detailed',f'week{week0}',weekrest, f'week{week0}_{weekrest}.czi')
        # Check if file exists
        print(czi_path)
        if not os.path.isfile(czi_path):
            abort(404)
        
        # Send the file as download
        return send_file(czi_path, as_attachment=True, download_name=f'detailweek{week}.czi')

@app.route('/download/detailweektif<string:week>')
def download_detailweektif(week):
    # Path to the CZI file
    week0= week[0]
    print(week)
    if week0 == 0:
        czi_path = os.path.join(app.static_folder, 'czi_images_detailed',f'week{week0}' f'week{week0}.tif')
        # Check if file exists
        print(czi_path)
        if not os.path.isfile(czi_path):
            abort(404)
        
        # Send the file as download
        return send_file(czi_path, as_attachment=True, download_name=f'detailweek{week0}.tif')
    else:
        weekrest= week[1:]

        czi_path = os.path.join(app.static_folder, 'czi_images_detailed',f'week{week0}',weekrest, f'week{week0}_{weekrest}.tif')
        print(czi_path)
        # Check if file exists
        if not os.path.isfile(czi_path):
            abort(404)
        
        # Send the file as download
        return send_file(czi_path, as_attachment=True, download_name=f'detailweek{week}.tif')
        
    

@app.route('/download/main/week<int:week>')
def download_main_detailweek(week):
    # Alternative route for main download (same functionality)
    return download_detailweek(week)

@app.route('/download/main/detailweek<int:week><string:iter>')
def download_main_detailweektf(week):
    # Alternative route for main download (same functionality)
    return download_detailweektif(week)

@app.route('/download/main/detailweektif<int:week><string:iter>')
def download_main_week(week):
    # Alternative route for main download (same functionality)
    return download_week(week)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
