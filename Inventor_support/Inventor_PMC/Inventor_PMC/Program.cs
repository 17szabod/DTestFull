using System;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using Inventor;

namespace Inventor_PMC
{
    class Program
    {
        static void Main(string[] args)
        {
            int density = int.Parse(args[1]);
            string filename = args[0];
            double pmc_param = double.Parse(args[2]);
            double sys_eps = 1e-5;
            Console.WriteLine($"Running Inventor PMC with parameters pmc_param: {pmc_param}, density: {density}");
            Application _invApp;
            Boolean _started = false;

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
                    _started = true;

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
            ComponentDefinition cdef = (ComponentDefinition)doc.ComponentDefinition;
            SurfaceBodies bodies = cdef.SurfaceBodies;
            //double x = 8.71;
            //double y = 0;
            //double z = 0;
            //int res = pmc(pmc_param, _invApp, bodies, x, y, z);
            //Debug.Print(res.ToString());
            if (bodies.Count > 1)
            {
                Debug.Print("DTest for Inventor does not yet support parts with multiple bodies.");
                Console.WriteLine("DTest for Inventor does not yet support parts with multiple bodies.");
                return;
            }
            SurfaceBody body = null;
            foreach (SurfaceBody tmp_body in bodies)
            {
                body = tmp_body;
            }
            //double minX, minY, minZ, maxX, maxY, maxZ;
            Point minpoint = body.RangeBox.MinPoint;
            Point maxpoint = body.RangeBox.MaxPoint;
            //body.RangeBox.GetBoxData(minpoint, maxpoint);
            double minX = minpoint.X;
            double minY = minpoint.Y;
            double minZ = minpoint.Z;
            double maxX = maxpoint.X;
            double maxY = maxpoint.Y;
            double maxZ = maxpoint.Z;
            double xh = (maxX - minX) / density;
            double yh = (maxY - minY) / density;
            double zh = (maxZ - minZ) / density;
            pmc_param /= 10;  // Manually convert from m to cm
            // Now that we have computed an approximate, expand the grid
            minX -= pmc_param;
            minY -= pmc_param;
            minZ -= pmc_param;
            maxX += pmc_param;
            maxY += pmc_param;
            maxZ += pmc_param;
            xh = (maxX - minX) / density;
            yh = (maxY - minY) / density;
            zh = (maxZ - minZ) / density;
            Debug.Print($"Bound box is {minX}, {minY}, {minZ}, {maxX}, {maxY}, {maxZ}");
            Console.WriteLine($"xh: {xh}, yh: {yh}, zh: {zh}");
            Console.WriteLine($"I am currently using pmc param of {pmc_param}, when the exact would be {Math.Sqrt(xh * xh + yh * yh + zh * zh) / 2 + sys_eps}");
            int[,,] pmc_results = new int[density + 1, density + 1, density + 1];

            double x, y, z;
            int count = 0;
            string out_string = "";  // out_string follows a format used by Rhino previously
            for (int a = 0; a <= density; a++)
            {
                x = minX + xh * a;
                for (int b = 0; b <= density; b++)
                {
                    y = minY + yh * b;
                    for (int c = 0; c <= density; c++)
                    {
                        count++;
                        z = minZ + zh * c;
                        if (count % (density * density) == 0)
                        {
                            Console.WriteLine($"Working on point ({x}, {y}, {z})");
                        }
                        pmc_results[a, b, c] = pmc(pmc_param, _invApp, bodies, x, y, z, body);
                        out_string += $"~{pmc_results[a, b, c]}$({10 * x}, {10 * y}, {10 * z})";  // Need to convert back to mm
                    }
                }
            }

            // Write pmc results to a shared file
            System.IO.File.WriteAllText(@"C:\Users\kisac\CLionProjects\DTestFull\temp_Inv_spheres.txt", out_string.Substring(1));

            return;
        }

        private static int pmc(double pmc_param, Application _invApp, SurfaceBodies bodies, double x, double y, double z, SurfaceBody body)
        {
            double[] coords = { x, y, z };
            Point p = _invApp.TransientGeometry.CreatePoint(x, y, z);
            double bod_dist = _invApp.MeasureTools.GetMinimumDistance(p, body, EntityOneInferredType: InferredTypeEnum.kInferredPoint);
            if (bod_dist == 0)  // We could be IN or ON, need to loop through faces to find the true distance
            {
                foreach (Face face in body.Faces)
                {
                    double dist = _invApp.MeasureTools.GetMinimumDistance(p, face, EntityOneInferredType: InferredTypeEnum.kInferredPoint);
                    if (dist < pmc_param)
                    {
                        return 0;
                    }
                }
                return 1;

            }
            if (bod_dist < pmc_param)
            {
                Debug.Print(bod_dist.ToString());
                return 0; //ON
            }
            return -1;
            //Debug.Print(min_dist.ToString());
            //ContainmentEnum res = closestBody.IsPointInside[coords, true];
            //if (res == ContainmentEnum.kUnknownContainment)
            //{
            //    Debug.Print("Failed to measure.");
            //    return -2;
            //}

            //return ContainmentEnum.kInsideContainment == res ? 1 : -1;
        }
    }
}
