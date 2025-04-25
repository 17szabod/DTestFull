using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using Inventor;

namespace Inventor_PMC
{
    class DisplayCloud
    {
        static void Main(string[] args)
        {
            string filename = @"C:\Users\danis\Coding\DTestFull\data\bunny.ipt";
            string shared_file = @"C:\Users\danis\Coding\DTestFull\temp_Inv_spheres.txt";
            Application _invApp;
            try
            {
                _invApp = (Application)Marshal.GetActiveObject("Inventor.Application");
            }
            catch (Exception ex)
            {
                try
                {
                    Type invAppType = Type.GetTypeFromProgID("Inventor.Application");
                    _invApp = (Application)Activator.CreateInstance(invAppType);
                    _invApp.Visible = true;

                }
                catch (Exception ex2)
                {
                    Console.WriteLine(ex2.ToString());
                    Console.WriteLine("Unable to get or start Inventor");
                    return;
                }
            }

            //PartDocument doc = (PartDocument)_invApp.ActiveDocument;
            PartDocument doc = (PartDocument)_invApp.Documents.Open(filename);
            PartComponentDefinition cdef = (PartComponentDefinition)doc.ComponentDefinition;
            Sketch3D insketch = cdef.Sketches3D.Add();
            Sketch3D onsketch = cdef.Sketches3D.Add();
            Sketch3D outsketch = cdef.Sketches3D.Add();
            
            string txt = System.IO.File.ReadAllText(shared_file);
            string[] points = txt.Split('~');
            foreach (string point in points)
            {
                string[] tmp = point.Split('$');
                int pmc = int.Parse(tmp[0]);
                double[] parr = Array.ConvertAll(tmp[1].Substring(1, tmp[1].Length - 2).Replace(" ", "").Split(','), Double.Parse);
                Point p = _invApp.TransientGeometry.CreatePoint(parr[0]/10, parr[1]/10, parr[2]/10);
                //Console.WriteLine($"Working on point ({tmp[0]}, {tmp[1]}), out count is {outsketch.SketchPoints3D.Count}");
                if (pmc == 1)
                {
                    insketch.SketchPoints3D.Add(p);
                }
                else if (pmc == 0)
                {
                    onsketch.SketchPoints3D.Add(p);
                }
                else if (pmc == -1)
                {
                    outsketch.SketchPoints3D.Add(p);
                }
            }
            var blue = _invApp.TransientObjects.CreateColor(0, 0, 255);
            var red = _invApp.TransientObjects.CreateColor(255, 0, 0);
            var green = _invApp.TransientObjects.CreateColor(0, 255, 255);

            insketch.OverrideColor = green;
            onsketch.OverrideColor = red;
            outsketch.OverrideColor = blue;
            _invApp.ActiveView.Update();
            _invApp.ActiveDocument.Update();
            return;
        }
        public void DrawPointCloud(PartComponentDefinition compDef, Application _invApp)
        {

            // Delete any previous graphics with same ID
            try
            {
                compDef.ClientGraphicsCollection["PointCloud"].Delete();
            }
            catch { }

            ClientGraphics clientGraphics = compDef.ClientGraphicsCollection.Add("PointCloud");
            GraphicsNode graphicsNode = clientGraphics.AddNode(1);

            // Create the coordinate set
            GraphicsCoordinateSet coordSet = compDef.GraphicsDataSetsCollection.CreateCoordinateSet("PointCloudCoords"); 
            //clientGraphics.CoordinateSets.Add(1);

            //GraphicsDataSets dataSets = compDef.GraphicsDataSetsCollection;
            GraphicsDataSetCoordinateSet coordSet = dataSets.CreateCoordinateSet("PointCoords");


            // Fill in your point cloud here (this is just example data)
            int pointCount = 1000;
            double[] coords = new double[pointCount * 3];

            for (int i = 0; i < pointCount; i++)
            {
                coords[3 * i] = i * 0.01;      // X
                coords[3 * i + 1] = 0;         // Y
                coords[3 * i + 2] = 0;         // Z
            }

            coordSet.PutCoordinates(ref coords);

            // Add the point graphics
            PointGraphics pointGraphics = graphicsNode.AddPointGraphics();
            pointGraphics.CoordinateSet = coordSet;
            pointGraphics.PointRenderStyle = PointRenderStyleEnum.kDotPointStyle;
            pointGraphics.Size = 0.05;
        }
}
