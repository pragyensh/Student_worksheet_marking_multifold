import cv2

img_path = 'backend/templates/week_07/template_image.jpg'
img = cv2.imread(img_path)

# Draw grid
h, w = img.shape[:2]
for x in range(0, w, 100):
    cv2.line(img, (x, 0), (x, h), (200, 200, 200), 1)
    cv2.putText(img, str(x), (x, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
for y in range(0, h, 100):
    cv2.line(img, (0, y), (w, y), (200, 200, 200), 1)
    cv2.putText(img, str(y), (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

cv2.imwrite('debug_grid.jpg', img)
